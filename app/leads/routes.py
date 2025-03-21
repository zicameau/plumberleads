from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from app import db
from app.leads import bp
from app.models.lead import Lead
from app.models.user import User
from app.models.payment import Payment
from app.routes.plumber import calculate_distance
from flask import current_app
import json
import stripe
from datetime import datetime
from flask_login import login_required
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/available')
def available():
    """Display available leads."""
    if not session.get('user'):
        flash('Please log in to view available leads.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get all available leads
    leads = Lead.query.filter_by(status='available').order_by(Lead.created_at.desc()).all()
    return render_template('leads/available.html', leads=leads)

@bp.route('/<uuid:lead_id>')
def view(lead_id):
    """View a specific lead."""
    if not session.get('user'):
        flash('Please log in to view lead details.', 'warning')
        return redirect(url_for('auth.login'))
    
    lead = Lead.query.get_or_404(lead_id)
    
    # Debug logging for lead data
    current_app.logger.info(f"View route - Lead ID: {lead.id}")
    current_app.logger.info(f"View route - Lead status: {lead.status}")
    current_app.logger.info(f"View route - Lead reserved_at: {lead.reserved_at}")
    current_app.logger.info(f"View route - Lead reserved_by_id: {lead.reserved_by_id}")
    
    # Calculate expiration time if lead is reserved
    expiration_timestamp = None
    if lead.status == 'reserved' and lead.reserved_at:
        expiry_minutes = current_app.config['LEAD_RESERVATION_EXPIRY_MINUTES']
        expiration_timestamp = int((lead.reserved_at.timestamp() + (expiry_minutes * 60)) * 1000)  # Convert to milliseconds for JS
        current_app.logger.info(f"View route - Calculated expiration timestamp: {expiration_timestamp}")
        current_app.logger.info(f"View route - Current time (ms): {int(datetime.utcnow().timestamp() * 1000)}")
        current_app.logger.info(f"View route - Time until expiration (minutes): {(expiration_timestamp/1000 - datetime.utcnow().timestamp())/60}")
    
    return render_template('leads/view.html', 
                         lead=lead,
                         expiration_timestamp=expiration_timestamp)

@bp.route('/<uuid:lead_id>/claim', methods=['POST'])
@login_required
def claim(lead_id):
    try:
        lead = Lead.query.get_or_404(lead_id)
        user = User.query.get(session.get('user_id'))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_verified():
            return jsonify({'error': 'Please verify your email address before claiming leads'}), 400

        if lead.status != 'available':
            return jsonify({'error': 'This lead is not available'}), 400

        # Check if lead is within service radius
        if user.latitude and user.longitude and lead.latitude and lead.longitude:
            distance = calculate_distance(
                user.latitude, user.longitude,
                lead.latitude, lead.longitude
            )
            if distance > user.service_radius:
                return jsonify({'error': 'This lead is outside your service area'}), 400

        # Initialize Stripe
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

        # Create payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(lead.price * 100),  # Convert to cents
            currency='usd',
            metadata={
                'lead_id': str(lead.id),
                'user_id': str(user.id)
            }
        )

        # Reserve the lead
        lead.reserve(user.id)

        # Create payment record
        payment = Payment(
            lead_id=lead.id,
            user_id=user.id,
            amount=lead.price,
            payment_intent_id=payment_intent.id,
            status='pending'
        )
        db.session.add(payment)

        db.session.commit()

        return jsonify({
            'client_secret': payment_intent.client_secret,
            'message': 'Lead reserved successfully'
        })

    except stripe.error.StripeError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reserving lead: {str(e)}")
        return jsonify({'error': 'An error occurred while reserving the lead'}), 500

@bp.route('/<uuid:lead_id>/reserve', methods=['POST'])
def reserve(lead_id):
    if 'user' not in session:
        flash('You must be logged in to reserve a lead.', 'error')
        return redirect(url_for('auth.login'))

    lead = Lead.query.get_or_404(lead_id)
    user_id = session['user']['id']

    try:
        # Check if user is verified using session data
        if not session['user'].get('email_confirmed_at'):
            flash('Your email must be verified before you can reserve leads. Please check your email for the verification link.', 'error')
            return redirect(url_for('leads.view', lead_id=lead_id))

        # Check if lead is available
        if lead.status != 'available':
            flash('This lead is no longer available.', 'error')
            return redirect(url_for('leads.view', lead_id=lead_id))

        # Reserve the lead
        lead.status = 'reserved'
        lead.reserved_by_id = user_id
        lead.reserved_at = datetime.utcnow()
        db.session.commit()

        expiry_minutes = current_app.config['LEAD_RESERVATION_EXPIRY_MINUTES']
        flash(f'Lead reserved successfully! You have {expiry_minutes} minutes to complete the payment before your reservation expires.', 'success')
        return redirect(url_for('leads.view', lead_id=lead_id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error reserving lead: {str(e)}')
        flash('An error occurred while reserving the lead.', 'error')
        return redirect(url_for('leads.view', lead_id=lead_id))

@bp.route('/<uuid:lead_id>/reservation-success')
@login_required
def reservation_success(lead_id):
    if not session.get('user'):
        flash('Please log in to view this page.', 'warning')
        return redirect(url_for('auth.login'))
        
    lead = Lead.query.get_or_404(lead_id)
    user = User.query.get(session['user']['id'])
    
    if not user or lead.reserved_by_id != user.id:
        flash('Invalid access.', 'error')
        return redirect(url_for('main.index'))
    
    # Debug logging for lead data
    current_app.logger.info(f"Lead ID: {lead.id}")
    current_app.logger.info(f"Lead reserved_at: {lead.reserved_at}")
    current_app.logger.info(f"Lead reserved_at type: {type(lead.reserved_at)}")
    
    # Calculate expiration time (15 minutes from reservation)
    if lead.reserved_at:
        expiration_timestamp = int((lead.reserved_at.timestamp() + (15 * 60)) * 1000)  # Convert to milliseconds for JS
        current_app.logger.info(f"Calculated expiration timestamp: {expiration_timestamp}")
        current_app.logger.info(f"Current time (ms): {int(datetime.utcnow().timestamp() * 1000)}")
        current_app.logger.info(f"Time until expiration (minutes): {(expiration_timestamp/1000 - datetime.utcnow().timestamp())/60}")
    else:
        current_app.logger.warning(f"No reservation time found for lead {lead.id}")
        expiration_timestamp = None
    
    return render_template('leads/reservation_success.html', 
                         lead=lead,
                         expiration_timestamp=expiration_timestamp)

@bp.route('/<uuid:lead_id>/payment', methods=['GET', 'POST'])
@login_required
def payment(lead_id):
    if not session.get('user'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('auth.login'))
        
    lead = Lead.query.get_or_404(lead_id)
    user = User.query.get(session['user']['id'])
    
    if not user or lead.reserved_by_id != user.id:
        flash('Invalid access.', 'error')
        return redirect(url_for('main.index'))
    
    if lead.status != 'reserved':
        flash('This lead is no longer reserved.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Initialize Stripe
            stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(lead.price * 100),  # Convert to cents
                currency=current_app.config['DEFAULT_CURRENCY'],
                metadata={
                    'lead_id': str(lead.id),
                    'user_id': str(user.id)
                }
            )
            
            # Create payment record
            payment = Payment(
                lead_id=lead.id,
                user_id=user.id,
                amount=lead.price,
                payment_intent_id=payment_intent.id,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            return render_template('leads/payment.html',
                                lead=lead,
                                payment=payment,
                                client_secret=payment_intent.client_secret)
            
        except Exception as e:
            current_app.logger.error(f"Error creating payment: {str(e)}")
            flash('An error occurred while processing your payment.', 'error')
            return redirect(url_for('leads.payment', lead_id=lead_id))
    
    return render_template('leads/payment.html', lead=lead)

@bp.route('/<uuid:lead_id>/release', methods=['POST'])
def release(lead_id):
    if 'user' not in session:
        flash('You must be logged in to release a lead.', 'error')
        return redirect(url_for('auth.login'))

    lead = Lead.query.get_or_404(lead_id)
    user_id = session['user']['id']

    try:
        # Check if the lead is reserved by the current user
        if lead.status != 'reserved' or lead.reserved_by_id != user_id:
            flash('You can only release leads that you have reserved.', 'error')
            return redirect(url_for('leads.view', lead_id=lead_id))

        # Release the lead
        lead.status = 'available'
        lead.reserved_by_id = None
        lead.reserved_at = None
        db.session.commit()

        flash('Lead released successfully.', 'success')
        return redirect(url_for('plumber.dashboard'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error releasing lead: {str(e)}')
        flash('An error occurred while releasing the lead.', 'error')
        return redirect(url_for('leads.view', lead_id=lead_id)) 
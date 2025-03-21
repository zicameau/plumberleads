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
from app.utils.pricing import calculate_lead_price

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
    
    # Calculate time left if lead is reserved
    time_left = None
    if lead.status == 'reserved' and lead.reserved_at:
        expiry_minutes = current_app.config['LEAD_RESERVATION_EXPIRY_MINUTES']
        expiration_time = lead.reserved_at.timestamp() + (expiry_minutes * 60)
        time_left = int(expiration_time - datetime.utcnow().timestamp())
        current_app.logger.info(f"View route - Time left (seconds): {time_left}")
    
    return render_template('leads/view.html', 
                         lead=lead,
                         time_left=time_left,
                         calculate_lead_price=calculate_lead_price)

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

        # Reserve the lead using the model's reserve method
        lead.reserve(user_id)

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

        # Release the lead using the model's release method
        lead.release()

        flash('Lead released successfully.', 'success')
        return redirect(url_for('leads.view', lead_id=lead_id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error releasing lead: {str(e)}')
        flash('An error occurred while releasing the lead.', 'error')
        return redirect(url_for('leads.view', lead_id=lead_id))

@bp.route('/<uuid:lead_id>/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session(lead_id):
    """Create a Stripe Checkout session."""
    try:
        lead = Lead.query.get_or_404(lead_id)
        user_id = session['user']['id']

        # Verify the lead is reserved by the current user
        if lead.status != 'reserved' or lead.reserved_by_id != user_id:
            return jsonify({'error': 'Invalid lead or not reserved by you'}), 400

        # Calculate the price using the utility function
        pricing = calculate_lead_price(lead.price)
        price_to_charge = pricing['lead_price']  # Access as dictionary

        # Initialize Stripe
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': lead.title,
                        'description': f"Lead for {lead.service_type} in {lead.city}, {lead.state} ({pricing['percentage']*100:.0f}% of total job price)",
                    },
                    'unit_amount': int(price_to_charge * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('leads.payment_success', lead_id=lead_id, _external=True),
            cancel_url=url_for('leads.view', lead_id=lead_id, _external=True),
            metadata={
                'lead_id': str(lead.id),
                'user_id': str(user_id)
            }
        )

        # Create payment record
        payment = Payment(
            lead_id=lead.id,
            user_id=user_id,
            amount=price_to_charge,
            currency='usd',
            payment_method='card',
            payment_processor='stripe',
            processor_payment_id=checkout_session.id,
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            'sessionId': checkout_session.id
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating checkout session: {str(e)}')
        return jsonify({'error': 'An error occurred while creating the checkout session'}), 500

@bp.route('/<uuid:lead_id>/payment-success')
@login_required
def payment_success(lead_id):
    """Handle successful payment."""
    try:
        lead = Lead.query.get_or_404(lead_id)
        user_id = session['user']['id']

        # Verify the lead is reserved by the current user
        if lead.status != 'reserved' or str(lead.reserved_by_id) != str(user_id):  # Convert both to strings for comparison
            flash('Invalid lead or not reserved by you', 'error')
            return redirect(url_for('leads.view', lead_id=lead_id))

        # Get the most recent payment for this lead
        payment = Payment.query.filter_by(
            lead_id=lead.id,
            user_id=user_id,
            status='pending'
        ).order_by(Payment.created_at.desc()).first()

        if not payment:
            current_app.logger.error(f"No pending payment found for lead {lead_id}")
            flash('No pending payment found.', 'error')
            return redirect(url_for('leads.view', lead_id=lead_id))

        # Update lead status and tracking
        lead.status = 'claimed'
        lead.claimed_at = datetime.utcnow()
        lead.claimed_by_id = user_id
        lead.contact_release_count += 1

        # Update payment status
        payment.status = 'completed'

        # Log the changes
        from app.utils.lead_history import log_lead_change
        log_lead_change(
            lead=lead,
            field_name='status',
            old_value='reserved',
            new_value='claimed',
            change_type='claim',
            user_id=user_id
        )

        db.session.commit()
        current_app.logger.info(f"Successfully claimed lead {lead_id}")

        flash('Payment successful! You can now view the customer contact information.', 'success')
            
        return redirect(url_for('leads.view', lead_id=lead_id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error in payment success route: {str(e)}')
        flash('An error occurred while processing the payment', 'error')
        return redirect(url_for('leads.view', lead_id=lead_id))

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    current_app.logger.info(f"Received webhook with signature header: {sig_header}")
    current_app.logger.info(f"Using webhook secret: {webhook_secret[:6]}...")  # Log first 6 chars for verification

    try:
        # Log the raw payload for debugging
        payload_str = payload.decode('utf-8')
        current_app.logger.info(f"Webhook payload: {payload_str}")
        
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        current_app.logger.info(f"Successfully verified webhook signature")
        current_app.logger.info(f"Webhook event type: {event['type']}")
        
        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Log the session data
            current_app.logger.info(f"Session data: {session}")
            
            # Get metadata
            metadata = session.get('metadata', {})
            current_app.logger.info(f"Session metadata: {metadata}")
            
            lead_id = metadata.get('lead_id')
            user_id = metadata.get('user_id')
            
            if not lead_id or not user_id:
                current_app.logger.error(f"Missing metadata - lead_id: {lead_id}, user_id: {user_id}")
                return jsonify({'error': 'Missing required metadata'}), 400

            try:
                lead = Lead.query.get(lead_id)
                if not lead:
                    current_app.logger.error(f"Lead not found: {lead_id}")
                    return jsonify({'error': 'Lead not found'}), 404

                if lead.status != 'reserved' or str(lead.reserved_by_id) != user_id:
                    current_app.logger.error(f"Invalid lead state or user: status={lead.status}, reserved_by={lead.reserved_by_id}, user_id={user_id}")
                    return jsonify({'error': 'Invalid lead state'}), 400

                # Create payment record
                payment = Payment(
                    lead_id=lead.id,
                    user_id=user_id,
                    amount=session['amount_total'] / 100,  # Convert from cents
                    currency=session['currency'],
                    payment_method='card',
                    payment_processor='stripe',
                    processor_payment_id=session['id'],
                    status='completed',
                    created_at=datetime.fromtimestamp(session['created'])
                )
                db.session.add(payment)

                # Update lead status and tracking
                lead.status = 'claimed'
                lead.claimed_at = datetime.utcnow()
                lead.claimed_by_id = user_id
                lead.contact_release_count += 1

                # Log the changes
                from app.utils.lead_history import log_lead_change
                log_lead_change(
                    lead=lead,
                    field_name='status',
                    old_value='reserved',
                    new_value='claimed',
                    change_type='claim',
                    user_id=user_id
                )

                db.session.commit()
                current_app.logger.info(f"Successfully processed payment and claimed lead {lead_id}")
                return jsonify({'status': 'success'})
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error processing webhook: {str(e)}")
                return jsonify({'error': str(e)}), 500

        # Return success for other event types
        return jsonify({'status': 'success'})

    except ValueError as e:
        current_app.logger.error(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"Invalid signature: {str(e)}")
        current_app.logger.error(f"Expected secret starting with: {webhook_secret[:6]}...")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500
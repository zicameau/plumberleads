from flask import render_template, redirect, url_for, flash, request, session, jsonify
from app import db
from app.leads import bp
from app.models.lead import Lead
from app.models.user import User
from flask import current_app
import json
import stripe
from datetime import datetime
from flask_login import login_required

@bp.route('/available')
def available():
    """Display available leads."""
    if not session.get('user'):
        flash('Please log in to view available leads.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get all unclaimed leads
    leads = Lead.query.filter_by(is_claimed=False).order_by(Lead.created_at.desc()).all()
    return render_template('leads/available.html', leads=leads)

@bp.route('/submit', methods=['GET', 'POST'])
def submit():
    """Submit a new lead."""
    if not session.get('user'):
        flash('Please log in to submit leads.', 'warning')
        return redirect(url_for('auth.login'))
    
    # TODO: Implement lead submission form and logic
    return render_template('leads/submit.html')

@bp.route('/<uuid:lead_id>')
def view(lead_id):
    """View a specific lead."""
    if not session.get('user'):
        flash('Please log in to view lead details.', 'warning')
        return redirect(url_for('auth.login'))
    
    lead = Lead.query.get_or_404(lead_id)
    return render_template('leads/view.html', lead=lead)

@bp.route('/<uuid:lead_id>/claim', methods=['POST'])
@login_required
def claim(lead_id):
    try:
        lead = Lead.query.get_or_404(lead_id)
        user = User.query.get(session.get('user_id'))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_verified:
            return jsonify({'error': 'Please verify your account before claiming leads'}), 400

        if lead.is_claimed:
            return jsonify({'error': 'This lead has already been claimed'}), 400

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

        # Update lead status
        lead.status = 'claimed'
        lead.plumber_id = user.id
        lead.claimed_at = datetime.utcnow()

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
            'message': 'Lead claimed successfully'
        })

    except stripe.error.StripeError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error claiming lead: {str(e)}")
        return jsonify({'error': 'An error occurred while claiming the lead'}), 500 
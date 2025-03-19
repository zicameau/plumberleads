from flask import jsonify, request, current_app
from flask_login import current_user, login_required
from app import db
from app.api import bp
from app.models.payment import Payment
from app.models.lead import Lead
import stripe
import os
from datetime import datetime

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Get payment history for current user
@bp.route('/payments', methods=['GET'])
@login_required
def get_payments():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # For admin, allow filtering by user_id
    if current_user.is_admin and request.args.get('user_id'):
        user_id = int(request.args.get('user_id'))
        query = Payment.query.filter_by(user_id=user_id)
    else:
        # Regular users can only see their own payments
        query = Payment.query.filter_by(user_id=current_user.id)
    
    # Apply filters if provided
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    
    # Date range filter
    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            query = query.filter(Payment.created_at >= start_date)
        except ValueError:
            pass
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date'))
            query = query.filter(Payment.created_at <= end_date)
        except ValueError:
            pass
    
    # Order by newest first
    query = query.order_by(Payment.created_at.desc())
    
    # Paginate results
    payments_page = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Transform to dictionary
    payments = [p.to_dict() for p in payments_page.items]
    
    return jsonify({
        'payments': payments,
        'total': payments_page.total,
        'pages': payments_page.pages,
        'page': page,
        'per_page': per_page
    })

# Get payment details by ID
@bp.route('/payments/<int:id>', methods=['GET'])
@login_required
def get_payment(id):
    payment = Payment.query.get_or_404(id)
    
    # Check if user is authorized to view this payment
    if not current_user.is_admin and payment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(payment.to_dict())

# Process a payment webhook from Stripe
@bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failure(payment_intent)
    
    return jsonify({'status': 'success'})

# Request a refund for a payment
@bp.route('/payments/<int:id>/refund', methods=['POST'])
@login_required
def request_refund(id):
    payment = Payment.query.get_or_404(id)
    
    # Check if user is authorized to request refund
    if not current_user.is_admin and payment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if payment is eligible for refund
    if payment.status != 'completed':
        return jsonify({'error': 'Only completed payments can be refunded'}), 400
    
    # If already refunded
    if payment.status == 'refunded':
        return jsonify({'error': 'Payment has already been refunded'}), 400
    
    data = request.get_json() or {}
    
    if 'reason' not in data:
        return jsonify({'error': 'Refund reason is required'}), 400
    
    try:
        # Process refund with Stripe
        refund = stripe.Refund.create(
            payment_intent=payment.processor_payment_id,
            reason='requested_by_customer'
        )
        
        # Update payment status
        payment.refund(data['reason'])
        
        # Update lead status if needed
        lead = Lead.query.get(payment.lead_id)
        if lead:
            lead.is_claimed = False
            lead.plumber_id = None
            lead.claimed_at = None
            lead.status = 'new'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Refund processed successfully',
            'payment': payment.to_dict(),
            'refund_id': refund.id
        })
    
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin endpoint to process a refund
@bp.route('/admin/payments/<int:id>/refund', methods=['POST'])
@login_required
def admin_refund(id):
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    payment = Payment.query.get_or_404(id)
    
    # Check if payment is eligible for refund
    if payment.status != 'completed':
        return jsonify({'error': 'Only completed payments can be refunded'}), 400
    
    # If already refunded
    if payment.status == 'refunded':
        return jsonify({'error': 'Payment has already been refunded'}), 400
    
    data = request.get_json() or {}
    
    if 'reason' not in data:
        return jsonify({'error': 'Refund reason is required'}), 400
    
    try:
        # Process refund with Stripe
        refund = stripe.Refund.create(
            payment_intent=payment.processor_payment_id,
            reason='fraudulent'  # Admin refunds marked as fraudulent for tracking
        )
        
        # Update payment status
        payment.refund(data['reason'])
        
        # Update lead status if needed
        lead = Lead.query.get(payment.lead_id)
        if lead:
            lead.is_claimed = False
            lead.plumber_id = None
            lead.claimed_at = None
            lead.status = 'new'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Refund processed successfully',
            'payment': payment.to_dict(),
            'refund_id': refund.id
        })
    
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Helper functions for webhook handling
def handle_payment_success(payment_intent):
    # Find the payment in our database
    payment = Payment.query.filter_by(processor_payment_id=payment_intent['id']).first()
    
    if payment:
        # Mark payment as completed
        payment.mark_as_completed()
        
        # Update any other necessary records
        db.session.commit()

def handle_payment_failure(payment_intent):
    # Find the payment in our database
    payment = Payment.query.filter_by(processor_payment_id=payment_intent['id']).first()
    
    if payment:
        # Mark payment as failed
        payment.mark_as_failed()
        
        # Revert lead claim
        lead = Lead.query.get(payment.lead_id)
        if lead:
            lead.is_claimed = False
            lead.plumber_id = None
            lead.claimed_at = None
            lead.status = 'new'
        
        db.session.commit() 
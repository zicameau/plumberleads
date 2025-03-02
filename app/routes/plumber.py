# app/routes/plumber.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, current_app
from app.services.auth_service import token_required, plumber_required
from app.services.lead_service import get_available_leads_for_plumber, claim_lead
from app.services.payment_service import (
    create_customer, create_subscription, create_checkout_session,
    create_lead_payment_intent, get_payment_methods
)
from app.models.plumber import Plumber
from app.models.lead import Lead
from app.models.lead_claim import LeadClaim

plumber_bp = Blueprint('plumber', __name__, url_prefix='/plumber')

# Service options for registration
PLUMBING_SERVICES = [
    {'id': 'emergency', 'name': 'Emergency Plumbing'},
    {'id': 'leak', 'name': 'Leak Detection & Repair'},
    {'id': 'drain', 'name': 'Drain Cleaning'},
    {'id': 'toilet', 'name': 'Toilet Repair/Installation'},
    {'id': 'faucet', 'name': 'Faucet Repair/Installation'},
    {'id': 'sink', 'name': 'Sink Repair/Installation'},
    {'id': 'disposal', 'name': 'Garbage Disposal Repair/Installation'},
    {'id': 'water_heater', 'name': 'Water Heater Services'},
    {'id': 'sewer', 'name': 'Sewer Line Services'},
    {'id': 'repiping', 'name': 'Repiping Services'},
    {'id': 'gas_line', 'name': 'Gas Line Installation/Repair'},
    {'id': 'backflow', 'name': 'Backflow Prevention'},
    {'id': 'waterproofing', 'name': 'Basement Waterproofing'},
    {'id': 'sump_pump', 'name': 'Sump Pump Services'},
    {'id': 'commercial', 'name': 'Commercial Plumbing'},
    {'id': 'inspection', 'name': 'Plumbing Inspection'},
    {'id': 'maintenance', 'name': 'Preventative Maintenance'},
    {'id': 'renovation', 'name': 'Bathroom/Kitchen Renovation Plumbing'},
    {'id': 'other', 'name': 'Other Plumbing Services'}
]

@plumber_bp.route('/', methods=['GET'])
@token_required
@plumber_required
def dashboard():
    """Plumber dashboard showing overview and stats."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            # If profile not complete, redirect to profile setup
            return redirect(url_for('plumber.complete_profile'))
        
        # Get recent leads claimed by this plumber
        recent_claims = LeadClaim.get_by_plumber(
            plumber_id=plumber.id,
            limit=5
        )
        
        # Get lead details for each claim
        claimed_leads = []
        for claim in recent_claims:
            lead = Lead.get_by_id(claim.lead_id)
            if lead:
                claimed_leads.append({
                    'lead': lead,
                    'claim': claim
                })
        
        # Get analytics/statistics
        # This would be a more complex query in a real application
        stats = {
            'leads_available': len(get_available_leads_for_plumber(plumber.id, limit=100)),
            'leads_claimed': len(LeadClaim.get_by_plumber(plumber.id)),
            'lead_credits': plumber.lead_credits,
            'subscription_status': plumber.subscription_status
        }
        
        return render_template('plumber/dashboard.html', 
                             plumber=plumber, 
                             stats=stats,
                             claimed_leads=claimed_leads)
    
    except Exception as e:
        current_app.logger.error(f"Error in plumber dashboard: {str(e)}")
        flash('An error occurred while loading your dashboard.', 'error')
        return render_template('plumber/dashboard.html', error=True)

@plumber_bp.route('/profile', methods=['GET', 'POST'])
@token_required
@plumber_required
def complete_profile():
    """Complete or update plumber profile."""
    try:
        # Check if plumber already has a profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if request.method == 'POST':
            # Process form submission
            plumber_data = {
                'user_id': g.user['id'],
                'company_name': request.form.get('company_name'),
                'contact_name': request.form.get('contact_name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'city': request.form.get('city'),
                'state': request.form.get('state'),
                'zip_code': request.form.get('zip_code'),
                'service_radius': int(request.form.get('service_radius', 25)),
                'services_offered': request.form.getlist('services_offered'),
                'license_number': request.form.get('license_number'),
                'is_insured': request.form.get('is_insured') == 'yes'
            }
            
            # Geocode the address
            from app.services.lead_service import geocode_address
            try:
                latitude, longitude = geocode_address(
                    plumber_data['address'],
                    plumber_data['city'],
                    plumber_data['state'],
                    plumber_data['zip_code']
                )
                plumber_data['latitude'] = latitude
                plumber_data['longitude'] = longitude
            except Exception as e:
                flash('Could not validate your address. Please check and try again.', 'error')
                return render_template('plumber/profile.html', 
                                     plumber=plumber_data,
                                     services=PLUMBING_SERVICES)
            
            if plumber:
                # Update existing profile
                for key, value in plumber_data.items():
                    setattr(plumber, key, value)
                plumber.save()
                
                flash('Your profile has been updated successfully.', 'success')
                return redirect(url_for('plumber.dashboard'))
            else:
                # Create new profile
                plumber = Plumber.create(plumber_data)
                
                if plumber:
                    flash('Your profile has been created successfully.', 'success')
                    return redirect(url_for('plumber.dashboard'))
                else:
                    flash('Failed to create your profile. Please try again.', 'error')
        
        # GET request or form submission failed
        return render_template('plumber/profile.html', 
                             plumber=plumber,
                             services=PLUMBING_SERVICES)
                             
    except Exception as e:
        current_app.logger.error(f"Error in complete_profile: {str(e)}")
        flash('An error occurred while processing your profile.', 'error')
        return render_template('plumber/profile.html', 
                             services=PLUMBING_SERVICES)

@plumber_bp.route('/leads', methods=['GET'])
@token_required
@plumber_required
def available_leads():
    """View available leads that match the plumber's criteria."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            # If profile not complete, redirect to profile setup
            return redirect(url_for('plumber.complete_profile'))
        
        # Check subscription status
        if plumber.subscription_status != 'active':
            flash('You need an active subscription to view leads.', 'warning')
            return redirect(url_for('plumber.subscription'))
        
        # Get available leads
        page = int(request.args.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page
        
        leads = get_available_leads_for_plumber(
            plumber_id=plumber.id,
            limit=per_page,
            offset=offset
        )
        
        # Check if there are more pages
        has_more = len(leads) == per_page
        
        return render_template('plumber/leads.html', 
                             plumber=plumber,
                             leads=leads,
                             page=page,
                             has_more=has_more,
                             lead_credits=plumber.lead_credits)
    
    except Exception as e:
        current_app.logger.error(f"Error in available_leads: {str(e)}")
        flash('An error occurred while loading available leads.', 'error')
        return render_template('plumber/leads.html', error=True)

@plumber_bp.route('/leads/<lead_id>/claim', methods=['POST'])
@token_required
@plumber_required
def claim_lead_route(lead_id):
    """Claim a lead."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            return jsonify({'success': False, 'error': 'Plumber profile not found'})
        
        # Check subscription status
        if plumber.subscription_status != 'active':
            return jsonify({'success': False, 'error': 'Active subscription required'})
        
        # Check if plumber has lead credits
        if plumber.lead_credits <= 0:
            return jsonify({'success': False, 'error': 'No lead credits available'})
        
        # Get notes from form
        notes = request.form.get('notes', '')
        
        # Process the claim
        claim = claim_lead(lead_id, plumber.id, notes)
        
        if claim:
            # Notify customer that their lead has been claimed
            from app.services.notification_service import send_lead_claimed_notification
            lead = Lead.get_by_id(lead_id)
            send_lead_claimed_notification(lead, plumber, notes)
            
            return jsonify({
                'success': True, 
                'message': 'Lead claimed successfully',
                'lead_credits_remaining': plumber.lead_credits
            })
        
        return jsonify({'success': False, 'error': 'Failed to claim lead'})
        
    except Exception as e:
        current_app.logger.error(f"Error in claim_lead: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@plumber_bp.route('/my-leads', methods=['GET'])
@token_required
@plumber_required
def my_leads():
    """View leads claimed by the plumber."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            # If profile not complete, redirect to profile setup
            return redirect(url_for('plumber.complete_profile'))
        
        # Get filter parameters
        status_filter = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        # Get claims based on filter
        if status_filter and status_filter != 'all':
            claims = LeadClaim.get_by_plumber(
                plumber_id=plumber.id,
                status=status_filter,
                limit=per_page,
                offset=offset
            )
        else:
            claims = LeadClaim.get_by_plumber(
                plumber_id=plumber.id,
                limit=per_page,
                offset=offset
            )
        
        # Get lead details for each claim
        claimed_leads = []
        for claim in claims:
            lead = Lead.get_by_id(claim.lead_id)
            if lead:
                claimed_leads.append({
                    'lead': lead,
                    'claim': claim
                })
        
        # Check if there are more pages
        has_more = len(claims) == per_page
        
        return render_template('plumber/my_leads.html', 
                             plumber=plumber,
                             claimed_leads=claimed_leads,
                             status_filter=status_filter,
                             page=page,
                             has_more=has_more)
    
    except Exception as e:
        current_app.logger.error(f"Error in my_leads: {str(e)}")
        flash('An error occurred while loading your leads.', 'error')
        return render_template('plumber/my_leads.html', error=True)

@plumber_bp.route('/my-leads/<claim_id>/update', methods=['POST'])
@token_required
@plumber_required
def update_lead_status(claim_id):
    """Update the status of a claimed lead."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            return jsonify({'success': False, 'error': 'Plumber profile not found'})
        
        # Get the claim
        claim = LeadClaim.get_by_id(claim_id)
        
        if not claim or claim.plumber_id != plumber.id:
            return jsonify({'success': False, 'error': 'Claim not found'})
        
        # Get form data
        new_status = request.form.get('status')
        contact_status = request.form.get('contact_status')
        notes = request.form.get('notes')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'})
        
        # Update the claim
        success = claim.update_status(new_status, contact_status, notes)
        
        if success:
            # If marking as completed, update the lead status too
            if new_status == 'completed':
                lead = Lead.get_by_id(claim.lead_id)
                if lead:
                    Lead.update_status(lead.id, 'completed')
            
            return jsonify({
                'success': True, 
                'message': 'Lead status updated successfully'
            })
        
        return jsonify({'success': False, 'error': 'Failed to update lead status'})
        
    except Exception as e:
        current_app.logger.error(f"Error in update_lead_status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@plumber_bp.route('/subscription', methods=['GET'])
@token_required
@plumber_required
def subscription():
    """View and manage subscription."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            # If profile not complete, redirect to profile setup
            return redirect(url_for('plumber.complete_profile'))
        
        # Get subscription details if active
        subscription_details = None
        if plumber.subscription_status == 'active' and plumber.stripe_subscription_id:
            from app.services.payment_service import get_stripe
            stripe = get_stripe()
            subscription_details = stripe.Subscription.retrieve(plumber.stripe_subscription_id)
        
        # Get payment methods
        payment_methods = []
        if plumber.stripe_customer_id:
            payment_methods = get_payment_methods(plumber.stripe_customer_id)
        
        return render_template('plumber/subscription.html', 
                             plumber=plumber,
                             subscription=subscription_details,
                             payment_methods=payment_methods,
                             monthly_price=current_app.config.get('MONTHLY_SUBSCRIPTION_PRICE_ID'))
    
    except Exception as e:
        current_app.logger.error(f"Error in subscription: {str(e)}")
        flash('An error occurred while loading your subscription details.', 'error')
        return render_template('plumber/subscription.html', error=True)

@plumber_bp.route('/subscription/checkout', methods=['POST'])
@token_required
@plumber_required
def create_subscription_checkout():
    """Create a Stripe Checkout session for subscription."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            return jsonify({'success': False, 'error': 'Plumber profile not found'})
        
        # Create or get Stripe customer
        if not plumber.stripe_customer_id:
            customer = create_customer(
                email=plumber.email,
                name=plumber.company_name,
                metadata={'plumber_id': plumber.id}
            )
            
            if not customer:
                return jsonify({'success': False, 'error': 'Failed to create customer'})
                
            plumber.stripe_customer_id = customer.id
            plumber.save()
        
        # Create checkout session
        price_id = current_app.config.get('MONTHLY_SUBSCRIPTION_PRICE_ID')
        success_url = url_for('plumber.subscription_success', _external=True)
        cancel_url = url_for('plumber.subscription', _external=True)
        
        checkout_session = create_checkout_session(
            customer_id=plumber.stripe_customer_id,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'plumber_id': plumber.id}
        )
        
        if not checkout_session:
            return jsonify({'success': False, 'error': 'Failed to create checkout session'})
            
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in create_subscription_checkout: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@plumber_bp.route('/subscription/success', methods=['GET'])
@token_required
@plumber_required
def subscription_success():
    """Handle successful subscription checkout."""
    # This page is shown after successful checkout
    # The actual subscription activation is handled by the Stripe webhook
    flash('Your subscription has been processed. It will be active shortly.', 'success')
    return redirect(url_for('plumber.subscription'))

@plumber_bp.route('/leads/purchase', methods=['GET', 'POST'])
@token_required
@plumber_required
def purchase_lead_credits():
    """Purchase additional lead credits."""
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(g.user['id'])
        
        if not plumber:
            # If profile not complete, redirect to profile setup
            return redirect(url_for('plumber.complete_profile'))
            
        if request.method == 'POST':
            # Process credit purchase
            credit_count = int(request.form.get('credit_count', 0))
            
            if credit_count <= 0:
                flash('Please select a valid number of credits to purchase.', 'error')
                return redirect(url_for('plumber.purchase_lead_credits'))
                
            # Calculate amount (e.g., $10 per credit)
            lead_price = current_app.config.get('LEAD_PRICE', 10.00)
            amount_cents = int(credit_count * lead_price * 100)  # Convert to cents
            
            # Create or get Stripe customer
            if not plumber.stripe_customer_id:
                customer = create_customer(
                    email=plumber.email,
                    name=plumber.company_name,
                    metadata={'plumber_id': plumber.id}
                )
                
                if not customer:
                    flash('Failed to process payment. Please try again.', 'error')
                    return redirect(url_for('plumber.purchase_lead_credits'))
                    
                plumber.stripe_customer_id = customer.id
                plumber.save()
            
            # Create payment intent
            payment_intent = create_lead_payment_intent(
                customer_id=plumber.stripe_customer_id,
                amount=amount_cents,
                metadata={
                    'plumber_id': plumber.id,
                    'credit_count': credit_count,
                    'type': 'lead_credit_purchase'
                }
            )
            
            if not payment_intent:
                flash('Failed to process payment. Please try again.', 'error')
                return redirect(url_for('plumber.purchase_lead_credits'))
                
            # Return payment page with client secret
            return render_template('plumber/payment.html',
                                 plumber=plumber,
                                 client_secret=payment_intent.client_secret,
                                 amount=lead_price * credit_count,
                                 credit_count=credit_count)
        
        # GET request - show purchase form
        return render_template('plumber/purchase_credits.html',
                             plumber=plumber,
                             lead_price=current_app.config.get('LEAD_PRICE', 10.00))
                             
    except Exception as e:
        current_app.logger.error(f"Error in purchase_lead_credits: {str(e)}")
        flash('An error occurred while processing your request.', 'error')
        return render_template('plumber/purchase_credits.html', error=True)

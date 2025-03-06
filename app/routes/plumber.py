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
import logging

# Get the app logger
logger = logging.getLogger('app')

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
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} accessing dashboard")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id}")
            flash('Please complete your profile to continue.', 'warning')
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
        
        logger.info(f"Plumber {user_id} dashboard loaded with {len(claimed_leads)} claimed leads")
        
        return render_template('plumber/dashboard.html', 
                             plumber=plumber, 
                             stats=stats,
                             claimed_leads=claimed_leads)
    
    except Exception as e:
        logger.error(f"Error in plumber dashboard for user {user_id}: {str(e)}", exc_info=True)
        flash('An error occurred while loading your dashboard.', 'error')
        return render_template('plumber/dashboard.html', error=True)

@plumber_bp.route('/profile', methods=['GET', 'POST'])
@token_required
@plumber_required
def complete_profile():
    """Complete or update plumber profile."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} accessing profile page")
    
    try:
        # Check if plumber already has a profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if request.method == 'POST':
            logger.info(f"Plumber {user_id} submitted profile form")
            
            # Process form submission
            plumber_data = {
                'user_id': user_id,
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
            
            logger.debug(f"Plumber profile data: {plumber_data}")
            
            # Geocode the address
            from app.services.lead_service import geocode_address
            try:
                logger.info(f"Geocoding address for plumber {user_id}")
                latitude, longitude = geocode_address(
                    plumber_data['address'],
                    plumber_data['city'],
                    plumber_data['state'],
                    plumber_data['zip_code']
                )
                plumber_data['latitude'] = latitude
                plumber_data['longitude'] = longitude
                logger.info(f"Geocoding successful: {latitude}, {longitude}")
            except Exception as e:
                logger.error(f"Geocoding failed for plumber {user_id}: {str(e)}", exc_info=True)
                flash('Could not validate your address. Please check and try again.', 'error')
                return render_template('plumber/profile.html', 
                                     plumber=plumber_data,
                                     services=PLUMBING_SERVICES)
            
            # Create or update plumber profile
            if plumber:
                logger.info(f"Updating existing plumber profile for {user_id}")
                # Update existing plumber
                for key, value in plumber_data.items():
                    setattr(plumber, key, value)
                plumber.save()
                flash('Profile updated successfully!', 'success')
            else:
                logger.info(f"Creating new plumber profile for {user_id}")
                # Create new plumber
                plumber = Plumber.create(plumber_data)
                if not plumber:
                    logger.error(f"Failed to create plumber profile for {user_id}")
                    flash('Could not create your profile. Please try again.', 'error')
                    return render_template('plumber/profile.html', 
                                         plumber=plumber_data,
                                         services=PLUMBING_SERVICES)
                flash('Profile created successfully!', 'success')
            
            logger.info(f"Plumber {user_id} profile saved successfully")
            return redirect(url_for('plumber.dashboard'))
        
        # GET request - show profile form
        logger.info(f"Displaying profile form for plumber {user_id}")
        return render_template('plumber/profile.html', 
                             plumber=plumber,
                             services=PLUMBING_SERVICES)
                             
    except Exception as e:
        logger.error(f"Error in plumber profile for user {user_id}: {str(e)}", exc_info=True)
        flash('An error occurred while processing your profile.', 'error')
        return render_template('plumber/profile.html', 
                             services=PLUMBING_SERVICES,
                             error=True)

@plumber_bp.route('/leads', methods=['GET'])
@token_required
@plumber_required
def available_leads():
    """View available leads that match the plumber's criteria."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} accessing available leads")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id}")
            flash('Please complete your profile to continue.', 'warning')
            return redirect(url_for('plumber.complete_profile'))
        
        # Check subscription status
        if plumber.subscription_status != 'active':
            logger.warning(f"Plumber {user_id} has inactive subscription")
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
        
        logger.info(f"Plumber {user_id} loaded {len(leads)} available leads")
        
        return render_template('plumber/leads.html', 
                             plumber=plumber,
                             leads=leads,
                             page=page,
                             has_more=has_more,
                             lead_credits=plumber.lead_credits)
    
    except Exception as e:
        logger.error(f"Error in available_leads for user {user_id}: {str(e)}", exc_info=True)
        flash('An error occurred while loading available leads.', 'error')
        return render_template('plumber/leads.html', error=True)

@plumber_bp.route('/leads/<lead_id>/claim', methods=['POST'])
@token_required
@plumber_required
def claim_lead_route(lead_id):
    """Claim a lead."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} attempting to claim lead {lead_id}")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id} attempting to claim lead")
            return jsonify({
                'success': False,
                'error': 'Plumber profile not found'
            }), 400
        
        # Check subscription status
        if plumber.subscription_status != 'active':
            logger.warning(f"Plumber {user_id} has inactive subscription")
            return jsonify({
                'success': False,
                'error': 'Active subscription required'
            }), 400
        
        # Check if plumber has lead credits
        if plumber.lead_credits <= 0:
            logger.warning(f"Plumber {user_id} has insufficient credits to claim lead {lead_id}")
            return jsonify({
                'success': False,
                'error': 'No lead credits available'
            }), 400
        
        # Get notes from form
        notes = request.form.get('notes', '')
        
        # Process the claim
        claim = claim_lead(lead_id, plumber.id, notes)
        
        if claim:
            # Notify customer that their lead has been claimed
            from app.services.notification_service import send_lead_claimed_notification
            lead = Lead.get_by_id(lead_id)
            send_lead_claimed_notification(lead, plumber, notes)
            
            # Deduct a credit
            plumber.lead_credits -= 1
            plumber.save()
            
            logger.info(f"Plumber {user_id} successfully claimed lead {lead_id}")
            return jsonify({
                'success': True, 
                'message': 'Lead claimed successfully',
                'remaining_credits': plumber.lead_credits
            })
        
        logger.warning(f"Plumber {user_id} failed to claim lead {lead_id}: Failed to claim lead")
        return jsonify({'success': False, 'error': 'Failed to claim lead'}), 400
        
    except Exception as e:
        logger.error(f"Error when plumber {user_id} attempted to claim lead {lead_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@plumber_bp.route('/my-leads', methods=['GET'])
@token_required
@plumber_required
def my_leads():
    """View leads claimed by the plumber."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} accessing my leads")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id}")
            flash('Please complete your profile to continue.', 'warning')
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
        
        logger.info(f"Plumber {user_id} loaded {len(claimed_leads)} claimed leads")
        
        return render_template('plumber/my_leads.html', 
                             plumber=plumber,
                             claimed_leads=claimed_leads,
                             status_filter=status_filter,
                             page=page,
                             has_more=has_more)
    
    except Exception as e:
        logger.error(f"Error in my_leads for user {user_id}: {str(e)}", exc_info=True)
        flash('An error occurred while loading your leads.', 'error')
        return render_template('plumber/my_leads.html', error=True)

@plumber_bp.route('/my-leads/<claim_id>/update', methods=['POST'])
@token_required
@plumber_required
def update_lead_status(claim_id):
    """Update the status of a claimed lead."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} attempting to update lead status for claim {claim_id}")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id}")
            return jsonify({'success': False, 'error': 'Plumber profile not found'}), 400
        
        # Get the claim
        claim = LeadClaim.get_by_id(claim_id)
        
        if not claim or claim.plumber_id != plumber.id:
            logger.warning(f"Claim {claim_id} not found for plumber {user_id}")
            return jsonify({'success': False, 'error': 'Claim not found'}), 400
        
        # Get form data
        new_status = request.form.get('status')
        contact_status = request.form.get('contact_status')
        notes = request.form.get('notes')
        
        if not new_status:
            logger.warning(f"Status is required for claim {claim_id}")
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        # Update the claim
        success = claim.update_status(new_status, contact_status, notes)
        
        if success:
            # If marking as completed, update the lead status too
            if new_status == 'completed':
                lead = Lead.get_by_id(claim.lead_id)
                if lead:
                    Lead.update_status(lead.id, 'completed')
            
            logger.info(f"Plumber {user_id} successfully updated lead status for claim {claim_id}")
            return jsonify({
                'success': True, 
                'message': 'Lead status updated successfully'
            })
        
        logger.warning(f"Plumber {user_id} failed to update lead status for claim {claim_id}")
        return jsonify({'success': False, 'error': 'Failed to update lead status'}), 400
        
    except Exception as e:
        logger.error(f"Error when plumber {user_id} attempted to update lead status for claim {claim_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@plumber_bp.route('/subscription', methods=['GET'])
@token_required
@plumber_required
def subscription():
    """View and manage subscription."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} accessing subscription")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id}")
            flash('Please complete your profile to continue.', 'warning')
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
        
        logger.info(f"Plumber {user_id} subscription loaded")
        
        return render_template('plumber/subscription.html', 
                             plumber=plumber,
                             subscription=subscription_details,
                             payment_methods=payment_methods,
                             monthly_price=current_app.config.get('MONTHLY_SUBSCRIPTION_PRICE_ID'))
    
    except Exception as e:
        logger.error(f"Error in subscription for user {user_id}: {str(e)}", exc_info=True)
        flash('An error occurred while loading your subscription details.', 'error')
        return render_template('plumber/subscription.html', error=True)

@plumber_bp.route('/subscription/checkout', methods=['POST'])
@token_required
@plumber_required
def create_subscription_checkout():
    """Create a Stripe Checkout session for subscription."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} attempting to create subscription checkout")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id}")
            return jsonify({'success': False, 'error': 'Plumber profile not found'}), 400
        
        # Create or get Stripe customer
        if not plumber.stripe_customer_id:
            logger.info(f"Creating new Stripe customer for plumber {user_id}")
            customer = create_customer(
                email=plumber.email,
                name=plumber.company_name,
                metadata={'plumber_id': plumber.id}
            )
            
            if not customer:
                logger.error(f"Failed to create Stripe customer for plumber {user_id}")
                return jsonify({'success': False, 'error': 'Failed to create customer'}), 500
                
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
            logger.error(f"Failed to create checkout session for plumber {user_id}")
            return jsonify({'success': False, 'error': 'Failed to create checkout session'}), 500
            
        logger.info(f"Plumber {user_id} successfully created checkout session")
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url
        })
        
    except Exception as e:
        logger.error(f"Error in create_subscription_checkout for user {user_id}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@plumber_bp.route('/subscription/success', methods=['GET'])
@token_required
@plumber_required
def subscription_success():
    """Handle successful subscription checkout."""
    # This page is shown after successful checkout
    # The actual subscription activation is handled by the Stripe webhook
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} accessing subscription success")
    
    flash('Your subscription has been processed. It will be active shortly.', 'success')
    return redirect(url_for('plumber.subscription'))

@plumber_bp.route('/leads/purchase', methods=['GET', 'POST'])
@token_required
@plumber_required
def purchase_lead_credits():
    """Purchase additional lead credits."""
    user_id = g.user.get('id')
    logger.info(f"Plumber {user_id} attempting to purchase lead credits")
    
    try:
        # Get plumber profile
        plumber = Plumber.get_by_user_id(user_id)
        
        if not plumber:
            logger.warning(f"No plumber profile found for user {user_id}")
            flash('Please complete your profile to continue.', 'warning')
            return redirect(url_for('plumber.complete_profile'))
            
        if request.method == 'POST':
            # Process credit purchase
            credit_count = int(request.form.get('credit_count', 0))
            
            if credit_count <= 0:
                logger.warning(f"Invalid credit count {credit_count} for plumber {user_id}")
                flash('Please select a valid number of credits to purchase.', 'error')
                return redirect(url_for('plumber.purchase_lead_credits'))
                
            # Calculate amount (e.g., $10 per credit)
            lead_price = current_app.config.get('LEAD_PRICE', 10.00)
            amount_cents = int(credit_count * lead_price * 100)  # Convert to cents
            
            # Create or get Stripe customer
            if not plumber.stripe_customer_id:
                logger.info(f"Creating new Stripe customer for plumber {user_id}")
                customer = create_customer(
                    email=plumber.email,
                    name=plumber.company_name,
                    metadata={'plumber_id': plumber.id}
                )
                
                if not customer:
                    logger.error(f"Failed to create Stripe customer for plumber {user_id}")
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
                logger.error(f"Failed to create payment intent for plumber {user_id}")
                flash('Failed to process payment. Please try again.', 'error')
                return redirect(url_for('plumber.purchase_lead_credits'))
                
            # Return payment page with client secret
            logger.info(f"Plumber {user_id} successfully created payment intent")
            return render_template('plumber/payment.html',
                                 plumber=plumber,
                                 client_secret=payment_intent.client_secret,
                                 amount=lead_price * credit_count,
                                 credit_count=credit_count)
        
        # GET request - show purchase form
        logger.info(f"Displaying purchase form for plumber {user_id}")
        return render_template('plumber/purchase_credits.html',
                             plumber=plumber,
                             lead_price=current_app.config.get('LEAD_PRICE', 10.00))
                             
    except Exception as e:
        logger.error(f"Error in purchase_lead_credits for user {user_id}: {str(e)}", exc_info=True)
        flash('An error occurred while processing your request.', 'error')
        return render_template('plumber/purchase_credits.html', error=True)

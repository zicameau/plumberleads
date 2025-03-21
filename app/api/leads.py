from flask import jsonify, request, current_app, session
from app import db
from app.api import bp
from app.models.lead import Lead
from app.models.payment import Payment
from app.models.user import User
from app.routes.plumber import calculate_distance
import stripe
import os
from functools import wraps

def get_current_user():
    """Get the current user from the session"""
    if not session.get('user'):
        return None
    return User.query.get(session['user']['id'])

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Get available leads for the current plumber
@bp.route('/leads', methods=['GET'])
@login_required
def get_leads():
    user = get_current_user()
    # Check if the user is a plumber
    if user.is_admin:
        # Admins can see all leads
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        query = Lead.query
        
        # Apply filters if provided
        if request.args.get('service_type'):
            query = query.filter_by(service_type=request.args.get('service_type'))
            
        if request.args.get('zip_code'):
            query = query.filter_by(zip_code=request.args.get('zip_code'))
            
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        
        # Order by newest first
        query = query.order_by(Lead.created_at.desc())
        
        # Paginate results
        leads_page = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Transform to dictionary
        leads = [lead.to_dict(include_contact=lead.status == 'claimed' and lead.claimed_by_id == user.id) 
                 for lead in leads_page.items]
        
        return jsonify({
            'leads': leads,
            'total': leads_page.total,
            'pages': leads_page.pages,
            'page': page,
            'per_page': per_page
        })
    else:
        # Regular plumbers can only see available leads in their service area
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Get user's service areas and service types
        service_areas = user.get_service_areas()
        service_types = user.get_service_types()
        
        # Base query for available leads
        query = Lead.query.filter_by(status='available')
        
        # Filter by service area if set
        if service_areas:
            query = query.filter(Lead.zip_code.in_(service_areas))
        
        # Filter by service type if set
        if service_types and request.args.get('filter_by_service_types', 'true').lower() == 'true':
            query = query.filter(Lead.service_type.in_(service_types))
        
        # Apply additional filters if provided
        if request.args.get('service_type'):
            query = query.filter_by(service_type=request.args.get('service_type'))
            
        if request.args.get('zip_code'):
            query = query.filter_by(zip_code=request.args.get('zip_code'))
        
        # Order by newest first
        query = query.order_by(Lead.created_at.desc())
        
        # Paginate results
        leads_page = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Transform to dictionary
        leads = [lead.to_dict(include_contact=False) for lead in leads_page.items]
        
        return jsonify({
            'leads': leads,
            'total': leads_page.total,
            'pages': leads_page.pages,
            'page': page,
            'per_page': per_page
        })

# Get claimed leads for the current plumber
@bp.route('/leads/claimed', methods=['GET'])
@login_required
def get_claimed_leads():
    user = get_current_user()
    # Check if the user is a plumber
    if user.is_admin:
        return jsonify({'error': 'This endpoint is only for plumbers'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Query for leads claimed by the current user
    query = Lead.query.filter_by(claimed_by_id=user.id)
    
    # Apply status filter if provided
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    
    # Order by newest first
    query = query.order_by(Lead.claimed_at.desc())
    
    # Paginate results
    leads_page = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Transform to dictionary
    leads = [lead.to_dict(include_contact=True) for lead in leads_page.items]
    
    return jsonify({
        'leads': leads,
        'total': leads_page.total,
        'pages': leads_page.pages,
        'page': page,
        'per_page': per_page
    })

# Get details of a specific lead
@bp.route('/leads/<int:id>', methods=['GET'])
@login_required
def get_lead(id):
    user = get_current_user()
    lead = Lead.query.get_or_404(id)
    
    # Check if the user is allowed to view this lead
    if not user.is_admin and lead.claimed_by_id != user.id and lead.status == 'claimed':
        return jsonify({'error': 'You are not authorized to view this lead'}), 403
    
    # Only include contact details if the lead is claimed by the current user or admin
    include_contact = user.is_admin or (lead.status == 'claimed' and lead.claimed_by_id == user.id)
    
    return jsonify(lead.to_dict(include_contact=include_contact))

# Reserve a lead
@bp.route('/leads/<uuid:id>/reserve', methods=['POST'])
@login_required
def reserve_lead(id):
    try:
        user = get_current_user()
        current_app.logger.info(f"Attempting to reserve lead {id} for user {user.id}")
        
        # Check if the user is a plumber
        if user.is_admin:
            current_app.logger.warning(f"Admin user {user.id} attempted to reserve lead {id}")
            return jsonify({'error': 'This endpoint is only for plumbers'}), 403
        
        lead = Lead.query.get_or_404(id)
        current_app.logger.info(f"Found lead {id} with status: {lead.status}")
        
        # Check if the lead is available
        if lead.status != 'available':
            current_app.logger.warning(f"Lead {id} is not available. Current status: {lead.status}")
            return jsonify({'error': 'This lead is not available'}), 400
        
        # Check if coordinates are available
        if not user.latitude or not user.longitude:
            current_app.logger.warning(f"User {user.id} has no location set")
            return jsonify({'error': 'Please update your location in your profile'}), 400
            
        if not lead.latitude or not lead.longitude:
            current_app.logger.warning(f"Lead {id} has no location set")
            return jsonify({'error': 'This lead has no location information'}), 400
        
        # Check if the lead is within service radius
        try:
            distance = calculate_distance(
                user.latitude, 
                user.longitude,
                lead.latitude,
                lead.longitude
            )
            current_app.logger.info(f"Distance to lead: {distance} miles, User service radius: {user.service_radius} miles")
            
            if distance > user.service_radius:
                current_app.logger.warning(f"Lead {id} is outside user {user.id}'s service radius")
                return jsonify({'error': 'Lead is outside your service area'}), 400
        except Exception as e:
            current_app.logger.error(f"Error calculating distance: {str(e)}")
            return jsonify({'error': 'Error calculating service area distance'}), 400
        
        # Initialize Stripe
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        try:
            current_app.logger.info(f"Creating Stripe payment intent for lead {id}")
            # Create a payment intent with Stripe
            payment_intent = stripe.PaymentIntent.create(
                amount=int(lead.price * 100),  # Convert to cents
                currency=current_app.config['DEFAULT_CURRENCY'],
                payment_method_types=['card'],
                description=f"Lead: {lead.title} (ID: {lead.id})",
                metadata={
                    'lead_id': str(lead.id),
                    'user_id': str(user.id)
                }
            )
            current_app.logger.info(f"Created Stripe payment intent: {payment_intent.id}")
            
            # Create a payment record
            payment = Payment(
                user_id=user.id,
                lead_id=lead.id,
                amount=lead.price,
                currency=current_app.config['DEFAULT_CURRENCY'],
                payment_method='card',
                payment_processor='stripe',
                processor_payment_id=payment_intent.id,
                payment_intent_id=payment_intent.id,
                client_secret=payment_intent.client_secret,
                status='pending'
            )
            
            # Reserve the lead
            lead.reserve(user.id)
            
            # Save changes to database
            db.session.add(payment)
            db.session.commit()
            current_app.logger.info(f"Successfully reserved lead {id} for user {user.id}")
            
            return jsonify({
                'message': 'Lead reserved successfully',
                'lead': lead.to_dict(),
                'payment': payment.to_dict()
            })
        
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe error while reserving lead {id}: {str(e)}")
            # Handle Stripe errors
            return jsonify({'error': str(e)}), 400
        
        except Exception as e:
            current_app.logger.error(f"Unexpected error while reserving lead {id}: {str(e)}")
            # Roll back transaction on error
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in reserve_lead route: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Complete payment and claim lead
@bp.route('/leads/<uuid:id>/complete-payment', methods=['POST'])
@login_required
def complete_payment(id):
    user = get_current_user()
    lead = Lead.query.get_or_404(id)
    payment = Payment.query.filter_by(lead_id=lead.id, user_id=user.id).first_or_404()
    
    # Check if the lead is still reserved for this user
    if lead.status != 'reserved' or lead.reserved_by_id != user.id:
        return jsonify({'error': 'Lead is no longer reserved for you'}), 400
    
    # Check if reservation has expired
    if lead.is_reservation_expired():
        lead.release()
        payment.mark_failed('Reservation expired')
        db.session.commit()
        return jsonify({'error': 'Lead reservation has expired'}), 400
    
    # Initialize Stripe
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        # Confirm the payment intent
        payment_intent = stripe.PaymentIntent.confirm(payment.payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            # Mark payment as completed
            payment.mark_completed()
            
            # Claim the lead
            lead.claim(user.id)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Payment completed and lead claimed successfully',
                'lead': lead.to_dict(include_contact=True),
                'payment': payment.to_dict()
            })
        else:
            payment.mark_failed('Payment not completed')
            db.session.commit()
            return jsonify({'error': 'Payment was not completed'}), 400
    
    except stripe.error.StripeError as e:
        payment.mark_failed(str(e))
        db.session.commit()
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Release a reserved lead
@bp.route('/leads/<uuid:id>/release', methods=['POST'])
@login_required
def release_lead(id):
    user = get_current_user()
    lead = Lead.query.get_or_404(id)
    
    # Check if the lead is reserved for this user
    if lead.status != 'reserved' or lead.reserved_by_id != user.id:
        return jsonify({'error': 'Lead is not reserved for you'}), 400
    
    try:
        # Release the lead
        lead.release()
        
        # Update payment status
        payment = Payment.query.filter_by(lead_id=lead.id, user_id=user.id).first()
        if payment:
            payment.mark_failed('Lead released by user')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lead released successfully',
            'lead': lead.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update lead status
@bp.route('/leads/<int:id>/status', methods=['PUT'])
@login_required
def update_lead_status(id):
    user = get_current_user()
    lead = Lead.query.get_or_404(id)
    
    # Check if the user is authorized to update this lead
    if not user.is_admin and lead.claimed_by_id != user.id:
        return jsonify({'error': 'You are not authorized to update this lead'}), 403
    
    data = request.get_json() or {}
    
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    # Update lead status
    if lead.update_status(data['status']):
        # Add notes if provided
        if 'notes' in data:
            lead.notes = data['notes']
        
        db.session.commit()
        return jsonify({
            'message': 'Lead status updated successfully',
            'lead': lead.to_dict(include_contact=True)
        })
    else:
        return jsonify({'error': 'Invalid status'}), 400

# Submit a new lead (public endpoint)
@bp.route('/leads/submit', methods=['POST'])
def submit_lead():
    data = request.get_json() or {}
    
    # Check required fields
    required_fields = [
        'title', 'description', 'customer_name', 'customer_email', 
        'customer_phone', 'address', 'city', 'state', 'zip_code', 
        'service_type'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Must include {field} field'}), 400
    
    # Create new lead
    lead = Lead(
        title=data['title'],
        description=data['description'],
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
        customer_phone=data['customer_phone'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        service_type=data['service_type'],
        service_details=data.get('service_details', ''),
        urgency=data.get('urgency', 'normal'),
        price=float(data.get('price', 20.0)),  # Default price is $20
        source=data.get('source', 'website')
    )
    
    # Save to database
    db.session.add(lead)
    db.session.commit()
    
    return jsonify({
        'message': 'Lead submitted successfully',
        'lead_id': lead.id
    }), 201

# Admin endpoint to manually create a lead
@bp.route('/admin/leads', methods=['POST'])
@login_required
def create_lead():
    user = get_current_user()
    # Check if the user is an admin
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    
    # Check required fields
    required_fields = [
        'title', 'description', 'customer_name', 'customer_email', 
        'customer_phone', 'address', 'city', 'state', 'zip_code', 
        'service_type', 'price'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Must include {field} field'}), 400
    
    # Create new lead
    lead = Lead(
        title=data['title'],
        description=data['description'],
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
        customer_phone=data['customer_phone'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        service_type=data['service_type'],
        service_details=data.get('service_details', ''),
        urgency=data.get('urgency', 'normal'),
        price=float(data['price']),
        source=data.get('source', 'manual')
    )
    
    # Save to database
    db.session.add(lead)
    db.session.commit()
    
    return jsonify({
        'message': 'Lead created successfully',
        'lead': lead.to_dict(include_contact=True)
    }), 201 
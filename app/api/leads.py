from flask import jsonify, request, current_app
from flask_login import current_user, login_required
from app import db
from app.api import bp
from app.models.lead import Lead
from app.models.payment import Payment
from app.models.user import User
import stripe
import os

# Get available leads for the current plumber
@bp.route('/leads', methods=['GET'])
@login_required
def get_leads():
    # Check if the user is a plumber
    if current_user.is_admin:
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
        
        # Include claimed status filter if specified
        if request.args.get('is_claimed') is not None:
            is_claimed = request.args.get('is_claimed').lower() == 'true'
            query = query.filter_by(is_claimed=is_claimed)
        
        # Order by newest first
        query = query.order_by(Lead.created_at.desc())
        
        # Paginate results
        leads_page = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Transform to dictionary
        leads = [lead.to_dict(include_contact=lead.is_claimed and lead.plumber_id == current_user.id) 
                 for lead in leads_page.items]
        
        return jsonify({
            'leads': leads,
            'total': leads_page.total,
            'pages': leads_page.pages,
            'page': page,
            'per_page': per_page
        })
    else:
        # Regular plumbers can only see unclaimed leads in their service area
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Get user's service areas and service types
        service_areas = current_user.get_service_areas()
        service_types = current_user.get_service_types()
        
        # Base query for unclaimed leads
        query = Lead.query.filter_by(is_claimed=False)
        
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
    # Check if the user is a plumber
    if current_user.is_admin:
        return jsonify({'error': 'This endpoint is only for plumbers'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Query for leads claimed by the current user
    query = Lead.query.filter_by(plumber_id=current_user.id)
    
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
    lead = Lead.query.get_or_404(id)
    
    # Check if the user is allowed to view this lead
    if not current_user.is_admin and lead.plumber_id != current_user.id and lead.is_claimed:
        return jsonify({'error': 'You are not authorized to view this lead'}), 403
    
    # Only include contact details if the lead is claimed by the current user or admin
    include_contact = current_user.is_admin or (lead.is_claimed and lead.plumber_id == current_user.id)
    
    return jsonify(lead.to_dict(include_contact=include_contact))

# Claim a lead
@bp.route('/leads/<int:id>/claim', methods=['POST'])
@login_required
def claim_lead(id):
    # Check if the user is a plumber
    if current_user.is_admin:
        return jsonify({'error': 'This endpoint is only for plumbers'}), 403
    
    lead = Lead.query.get_or_404(id)
    
    # Check if the lead is already claimed
    if lead.is_claimed:
        return jsonify({'error': 'This lead is already claimed'}), 400
    
    # Initialize Stripe
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    
    try:
        # Create a payment intent with Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=int(lead.price * 100),  # Convert to cents for Stripe
            currency=os.environ.get('DEFAULT_CURRENCY', 'USD'),
            payment_method_types=['card'],
            description=f"Lead: {lead.title} (ID: {lead.id})",
            metadata={
                'lead_id': lead.id,
                'user_id': current_user.id
            }
        )
        
        # Create a payment record
        payment = Payment(
            user_id=current_user.id,
            lead_id=lead.id,
            amount=lead.price,
            currency=os.environ.get('DEFAULT_CURRENCY', 'USD'),
            payment_processor='stripe',
            processor_payment_id=payment_intent.id,
            status='pending'
        )
        
        # Claim the lead for the user
        lead.claim(current_user.id)
        
        # Save changes to database
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Lead claimed successfully',
            'lead': lead.to_dict(include_contact=True),
            'payment': payment.to_dict(),
            'client_secret': payment_intent.client_secret
        })
    
    except stripe.error.StripeError as e:
        # Handle Stripe errors
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        # Roll back transaction on error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update lead status
@bp.route('/leads/<int:id>/status', methods=['PUT'])
@login_required
def update_lead_status(id):
    lead = Lead.query.get_or_404(id)
    
    # Check if the user is authorized to update this lead
    if not current_user.is_admin and lead.plumber_id != current_user.id:
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
    # Check if the user is an admin
    if not current_user.is_admin:
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
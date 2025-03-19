from flask import jsonify, request
from flask_login import current_user, login_required
from app import db
from app.api import bp
from app.models.user import User
from app.models.lead import Lead
import json

# Get all plumbers (admin only)
@bp.route('/plumbers', methods=['GET'])
@login_required
def get_plumbers():
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    query = User.query.filter_by(is_admin=False)
    
    # Apply filters if provided
    if request.args.get('is_verified') is not None:
        is_verified = request.args.get('is_verified').lower() == 'true'
        query = query.filter_by(is_verified=is_verified)
        
    if request.args.get('is_active') is not None:
        is_active = request.args.get('is_active').lower() == 'true'
        query = query.filter_by(is_active=is_active)
    
    # Order by newest first
    query = query.order_by(User.created_at.desc())
    
    # Paginate results
    plumbers_page = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Transform to dictionary
    plumbers = [p.to_dict() for p in plumbers_page.items]
    
    return jsonify({
        'plumbers': plumbers,
        'total': plumbers_page.total,
        'pages': plumbers_page.pages,
        'page': page,
        'per_page': per_page
    })

# Get plumber profile
@bp.route('/plumbers/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify(current_user.to_dict())

# Update plumber profile
@bp.route('/plumbers/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json() or {}
    
    # Update basic profile fields
    allowed_fields = [
        'full_name', 'company_name', 'phone', 'business_description', 
        'profile_image', 'license_number'
    ]
    
    for field in allowed_fields:
        if field in data:
            setattr(current_user, field, data[field])
    
    # Update service areas if provided
    if 'service_areas' in data:
        current_user.set_service_areas(data['service_areas'])
    
    # Update service types if provided
    if 'service_types' in data:
        current_user.set_service_types(data['service_types'])
    
    # Update insurance status if provided
    if 'has_insurance' in data:
        current_user.has_insurance = bool(data['has_insurance'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    })

# Get plumber by ID (admin only)
@bp.route('/plumbers/<int:id>', methods=['GET'])
@login_required
def get_plumber(id):
    # Check if user is admin
    if not current_user.is_admin and current_user.id != id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    plumber = User.query.get_or_404(id)
    
    # Return plumber details along with summary stats
    plumber_dict = plumber.to_dict()
    
    # Add summary stats if admin
    if current_user.is_admin:
        # Count claimed leads
        claimed_leads = Lead.query.filter_by(plumber_id=id).count()
        
        # Add stats to response
        plumber_dict.update({
            'stats': {
                'claimed_leads': claimed_leads
            }
        })
    
    return jsonify(plumber_dict)

# Update plumber status (admin only)
@bp.route('/plumbers/<int:id>/status', methods=['PUT'])
@login_required
def update_plumber_status(id):
    # Check if user is admin
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    plumber = User.query.get_or_404(id)
    data = request.get_json() or {}
    
    # Update active status if provided
    if 'is_active' in data:
        plumber.is_active = bool(data['is_active'])
    
    # Update verification status if provided
    if 'is_verified' in data:
        plumber.is_verified = bool(data['is_verified'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Plumber status updated successfully',
        'plumber': plumber.to_dict()
    })

# Get service area options
@bp.route('/service-areas', methods=['GET'])
def get_service_areas():
    # This would typically come from a database table
    # For now, we'll provide a static list as an example
    service_areas = [
        {"id": "90001", "name": "Los Angeles - Downtown"},
        {"id": "90210", "name": "Beverly Hills"},
        {"id": "90401", "name": "Santa Monica"},
        {"id": "92101", "name": "San Diego - Downtown"},
        {"id": "94102", "name": "San Francisco - Downtown"},
        {"id": "94301", "name": "Palo Alto"}
    ]
    
    return jsonify(service_areas)

# Get service type options
@bp.route('/service-types', methods=['GET'])
def get_service_types():
    # This would typically come from a database table
    # For now, we'll provide a static list as an example
    service_types = [
        {"id": "emergency", "name": "Emergency Repairs"},
        {"id": "drain", "name": "Drain Cleaning"},
        {"id": "water_heater", "name": "Water Heater Installation/Repair"},
        {"id": "pipe", "name": "Pipe Installation/Repair"},
        {"id": "fixture", "name": "Fixture Installation"},
        {"id": "remodeling", "name": "Remodeling Plumbing"},
        {"id": "commercial", "name": "Commercial Plumbing"},
        {"id": "residential", "name": "Residential Plumbing"}
    ]
    
    return jsonify(service_types) 
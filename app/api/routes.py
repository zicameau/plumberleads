from flask import jsonify, request
from ..utils.auth_middleware import require_auth
from . import api_bp
from ..services.lead_service import LeadService
from ..utils.errors import ValidationError, NotFoundError

@api_bp.route('/protected')
@require_auth
def protected():
    """Test protected route"""
    return jsonify({
        "message": "Access granted",
        "user": request.user
    })

@api_bp.route('/leads', methods=['POST'])
@require_auth
def create_lead():
    """Create a new lead"""
    data = request.get_json()
    if not data:
        return jsonify({"error": {"message": "No data provided"}}), 400
    
    try:
        result = LeadService.create_lead(data)
        return jsonify(result), 201
    except ValidationError as e:
        error_message = str(e) or "Missing required field"
        return jsonify({"error": {"message": error_message}}), 400
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@api_bp.route('/leads/<lead_id>', methods=['GET'])
@require_auth
def get_lead(lead_id):
    """Get a lead by ID"""
    try:
        result = LeadService.get_lead(lead_id)
        return jsonify(result)
    except NotFoundError as e:
        error_message = str(e) or f"Lead not found with ID: {lead_id}"
        return jsonify({"error": {"message": error_message}}), 404
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@api_bp.route('/leads/<lead_id>', methods=['PUT'])
@require_auth
def update_lead(lead_id):
    """Update a lead"""
    data = request.get_json()
    if not data:
        return jsonify({"error": {"message": "No data provided"}}), 400
    
    try:
        result = LeadService.update_lead(lead_id, data)
        return jsonify(result)
    except NotFoundError as e:
        error_message = str(e) or f"Lead not found with ID: {lead_id}"
        return jsonify({"error": {"message": error_message}}), 404
    except ValidationError as e:
        error_message = str(e) or "Invalid update data"
        return jsonify({"error": {"message": error_message}}), 400
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@api_bp.route('/leads', methods=['GET'])
@require_auth
def list_leads():
    """List leads with optional filtering and pagination"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get filter parameters
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('zip_code'):
        filters['zip_code'] = request.args.get('zip_code')
    if request.args.get('plumber_id'):
        filters['plumber_id'] = request.args.get('plumber_id')
    
    try:
        result = LeadService.list_leads(filters, page, per_page)
        return jsonify(result)
    except ValidationError as e:
        error_message = str(e) or "Invalid filter parameters"
        return jsonify({"error": {"message": error_message}}), 400
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@api_bp.route('/leads/<lead_id>/assign', methods=['POST'])
@require_auth
def assign_lead(lead_id):
    """Assign a lead to a plumber"""
    data = request.get_json()
    if not data or 'plumber_id' not in data:
        return jsonify({"error": {"message": "Plumber ID is required"}}), 400
    
    try:
        result = LeadService.assign_lead(lead_id, data['plumber_id'])
        return jsonify(result)
    except NotFoundError as e:
        error_message = str(e) or f"Lead or plumber not found"
        return jsonify({"error": {"message": error_message}}), 404
    except ValidationError as e:
        error_message = str(e) or "Invalid assignment data"
        return jsonify({"error": {"message": error_message}}), 400
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

@api_bp.route('/leads/<lead_id>/status', methods=['PUT'])
@require_auth
def update_lead_status(lead_id):
    """Update a lead's status"""
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": {"message": "Status is required"}}), 400
    
    try:
        result = LeadService.update_lead_status(lead_id, data['status'])
        return jsonify(result)
    except NotFoundError as e:
        error_message = str(e) or f"Lead not found with ID: {lead_id}"
        return jsonify({"error": {"message": error_message}}), 404
    except ValidationError as e:
        error_message = str(e) or "Invalid status. Must be one of: new, assigned, in_progress, completed, cancelled"
        return jsonify({"error": {"message": error_message}}), 400
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500 
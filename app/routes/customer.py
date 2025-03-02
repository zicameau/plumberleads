# app/routes/customer.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from app.services.lead_service import process_new_lead, GeocodingError
import logging

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

# Service options for the form
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

# Urgency options for the form
URGENCY_OPTIONS = [
    {'id': 'emergency', 'name': 'Emergency (As soon as possible)'},
    {'id': 'today', 'name': 'Today'},
    {'id': 'tomorrow', 'name': 'Tomorrow'},
    {'id': 'this_week', 'name': 'This week'},
    {'id': 'next_week', 'name': 'Next week'},
    {'id': 'flexible', 'name': 'Flexible (Within the next few weeks)'}
]

@customer_bp.route('/', methods=['GET'])
def index():
    """Customer home page."""
    return redirect(url_for('customer.request_service'))

@customer_bp.route('/request', methods=['GET', 'POST'])
def request_service():
    """Service request form page."""
    if request.method == 'POST':
        try:
            # Collect form data
            lead_data = {
                'customer_name': request.form.get('name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'city': request.form.get('city'),
                'state': request.form.get('state'),
                'zip_code': request.form.get('zip_code'),
                'problem_description': request.form.get('problem_description'),
                'service_needed': request.form.getlist('service_needed'),
                'urgency': request.form.get('urgency')
            }
            
            # Process the lead
            lead, matching_plumbers = process_new_lead(lead_data)
            
            # Store lead ID in session for confirmation page
            if lead and lead.id:
                request.session['lead_id'] = lead.id
                
                # Redirect to confirmation page
                return redirect(url_for('customer.request_confirmation'))
            else:
                # Handle case where lead processing failed
                flash('We encountered an issue processing your request. Please try again.', 'error')
                return render_template('customer/form.html', 
                                     services=PLUMBING_SERVICES,
                                     urgency_options=URGENCY_OPTIONS,
                                     form_data=lead_data)
                
        except GeocodingError:
            # Handle address geocoding errors
            flash('We could not locate your address. Please check your address information and try again.', 'error')
            return render_template('customer/form.html', 
                                 services=PLUMBING_SERVICES,
                                 urgency_options=URGENCY_OPTIONS,
                                 form_data=request.form)
                                 
        except Exception as e:
            # Log any other errors
            current_app.logger.error(f"Error in request_service: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('customer/form.html', 
                                 services=PLUMBING_SERVICES,
                                 urgency_options=URGENCY_OPTIONS,
                                 form_data=request.form)
    
    # GET request - show the form
    return render_template('customer/form.html', 
                         services=PLUMBING_SERVICES,
                         urgency_options=URGENCY_OPTIONS)

@customer_bp.route('/confirmation', methods=['GET'])
def request_confirmation():
    """Confirmation page after submitting a service request."""
    # Get lead ID from session
    lead_id = request.session.get('lead_id')
    
    if not lead_id:
        # If no lead ID in session, redirect to request form
        return redirect(url_for('customer.request_service'))
    
    # Clear lead ID from session to prevent revisiting
    request.session.pop('lead_id', None)
    
    # Get lead details for confirmation
    from app.models.lead import Lead
    lead = Lead.get_by_id(lead_id)
    
    if not lead:
        # If lead not found, redirect to request form
        flash('We could not find your service request. Please submit a new request.', 'error')
        return redirect(url_for('customer.request_service'))
    
    return render_template('customer/confirmation.html', lead=lead)

@customer_bp.route('/api/request', methods=['POST'])
def api_request_service():
    """API endpoint for submitting service requests programmatically."""
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code', 
                          'problem_description', 'service_needed', 'urgency']
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Process the lead
        lead, matching_plumbers = process_new_lead(data)
        
        # Return success response
        return jsonify({
            'success': True,
            'lead_id': lead.id,
            'message': 'Service request submitted successfully',
            'matching_plumbers_count': len(matching_plumbers)
        })
        
    except GeocodingError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'geocoding_error'
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"API error in request_service: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred',
            'error_type': 'server_error'
        }), 500

@customer_bp.route('/track/<lead_reference>', methods=['GET'])
def track_request(lead_reference):
    """Page for customers to track the status of their service request."""
    try:
        from app.models.lead import Lead
        
        # Look up the lead by reference code
        lead = Lead.get_by_reference(lead_reference)
        
        if not lead:
            flash('Service request not found. Please check the reference code and try again.', 'error')
            return render_template('customer/track.html', lead=None)
        
        # Get the plumbers who claimed this lead
        from app.models.lead_claim import LeadClaim
        from app.models.plumber import Plumber
        
        claims = LeadClaim.get_by_lead(lead.id)
        plumbers = []
        
        for claim in claims:
            plumber = Plumber.get_by_id(claim.plumber_id)
            if plumber:
                plumbers.append({
                    'company_name': plumber.company_name,
                    'contact_name': plumber.contact_name,
                    'phone': plumber.phone,
                    'email': plumber.email,
                    'claimed_at': claim.claimed_at,
                    'status': claim.status,
                    'notes': claim.notes
                })
        
        return render_template('customer/track.html', lead=lead, plumbers=plumbers)
        
    except Exception as e:
        current_app.logger.error(f"Error in track_request: {str(e)}")
        flash('An error occurred while retrieving your service request.', 'error')
        return render_template('customer/track.html', lead=None)
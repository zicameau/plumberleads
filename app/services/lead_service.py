# app/services/lead_service.py
import json
import requests
from flask import current_app
from datetime import datetime
import os
import logging

from app.models.lead import Lead
from app.models.plumber import Plumber
from app.models.lead_claim import LeadClaim
from app.services.notification_service import send_plumber_notification, send_customer_confirmation

# Get the app logger
logger = logging.getLogger('app')

class GeocodingError(Exception):
    """Exception raised when geocoding fails."""
    pass


def geocode_address(address, city, state, zip_code):
    """
    Convert address to latitude and longitude using a geocoding service.
    
    Args:
        address: Street address
        city: City name
        state: State or province
        zip_code: Postal code
        
    Returns:
        Tuple of (latitude, longitude) if successful
        
    Raises:
        GeocodingError: If geocoding fails
    """
    logger.info(f"Geocoding address: {address}, {city}, {state} {zip_code}")
    
    try:
        # Format the address for the geocoding API
        formatted_address = f"{address}, {city}, {state} {zip_code}"
        
        # Use a geocoding service (Google Maps, Mapbox, etc.)
        # This is a simplified example using Nominatim (OpenStreetMap)
        # In production, use a paid service with better rate limits
        
        # Replace with your preferred geocoding service
        api_key = os.environ.get('GEOCODING_API_KEY', '')
        
        if api_key:
            # Example using Google Maps Geocoding API
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={formatted_address}&key={api_key}"
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                latitude = location['lat']
                longitude = location['lng']
                logger.info(f"Geocoding successful: {latitude}, {longitude}")
                return latitude, longitude
            else:
                logger.warning(f"Geocoding failed with status: {data['status']}")
                raise ValueError(f"Geocoding failed: {data['status']}")
        else:
            # Fallback to Nominatim (use only for development)
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={formatted_address}"
            headers = {'User-Agent': 'PlumberLeads/1.0'}
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if data and len(data) > 0:
                latitude = float(data[0]['lat'])
                longitude = float(data[0]['lon'])
                logger.info(f"Geocoding successful (fallback): {latitude}, {longitude}")
                return latitude, longitude
            else:
                logger.warning("Geocoding failed: No results found")
                raise ValueError("Geocoding failed: No results found")
    except Exception as e:
        logger.error(f"Geocoding error: {str(e)}", exc_info=True)
        raise


def process_new_lead(lead_data):
    """
    Process a new customer lead, including geocoding and finding matching plumbers.
    
    Args:
        lead_data: Dictionary with lead information
        
    Returns:
        Tuple of (lead, matching_plumbers) if successful
    """
    try:
        # Geocode the address
        latitude, longitude = geocode_address(
            lead_data['address'],
            lead_data['city'],
            lead_data['state'],
            lead_data['zip_code']
        )
        
        # Add coordinates to lead data
        lead_data['latitude'] = latitude
        lead_data['longitude'] = longitude
        
        # Create the lead in the database
        lead = Lead.create(lead_data)
        
        if not lead:
            raise Exception("Failed to create lead in database")
        
        # Find matching plumbers in the area
        radius = current_app.config.get('LEAD_RADIUS_MILES', 25)
        services_needed = lead_data.get('service_needed', [])
        
        matching_plumbers = Plumber.find_by_location(
            latitude=latitude,
            longitude=longitude,
            radius_miles=radius,
            services=services_needed
        )
        
        # Send notification to matching plumbers
        for plumber in matching_plumbers:
            send_plumber_notification(plumber, lead)
        
        # Send confirmation to customer
        send_customer_confirmation(lead)
        
        return lead, matching_plumbers
        
    except GeocodingError as e:
        current_app.logger.error(f"Geocoding error in lead processing: {str(e)}")
        raise
    except Exception as e:
        current_app.logger.error(f"Error processing lead: {str(e)}")
        raise


def claim_lead(lead_id, plumber_id, notes=None):
    """
    Process a plumber claiming a lead.
    
    Args:
        lead_id: ID of the lead being claimed
        plumber_id: ID of the plumber claiming the lead
        notes: Optional notes from plumber
        
    Returns:
        LeadClaim object if successful
    """
    logger.info(f"Plumber {plumber_id} attempting to claim lead {lead_id}")
    
    try:
        # Check if lead exists and is available
        lead = Lead.get_by_id(lead_id)
        if not lead:
            logger.warning(f"Lead {lead_id} not found during claim attempt")
            return {
                'success': False,
                'error': 'Lead not found'
            }
            
        if lead.status != 'new' and lead.status != 'matched':
            logger.warning(f"Lead {lead_id} is not available (status: {lead.status})")
            return {
                'success': False,
                'error': f"Lead {lead_id} is not available (status: {lead.status})"
            }
        
        # Check if plumber exists and can claim leads
        plumber = Plumber.get_by_id(plumber_id)
        if not plumber:
            logger.warning(f"Plumber {plumber_id} not found during lead claim attempt")
            return {
                'success': False,
                'error': 'Plumber not found'
            }
            
        if plumber.subscription_status != 'active':
            logger.warning(f"Plumber {plumber_id} does not have an active subscription")
            return {
                'success': False,
                'error': f"Plumber {plumber_id} does not have an active subscription"
            }
            
        if plumber.lead_credits <= 0:
            logger.warning(f"Plumber {plumber_id} has no lead credits remaining")
            return {
                'success': False,
                'error': f"Plumber {plumber_id} has no lead credits remaining"
            }
        
        # Check if plumber has already claimed this lead
        existing_claim = LeadClaim.get_by_lead_and_plumber(lead_id, plumber_id)
        if existing_claim:
            logger.warning(f"Plumber {plumber_id} has already claimed lead {lead_id}")
            return {
                'success': False,
                'error': f"Plumber {plumber_id} has already claimed lead {lead_id}"
            }
        
        # Deduct a lead credit
        if not plumber.use_lead_credit():
            logger.warning(f"Failed to deduct lead credit for plumber {plumber_id}")
            return {
                'success': False,
                'error': f"Failed to deduct lead credit for plumber {plumber_id}"
            }
        
        # Create the lead claim
        claim_data = {
            'lead_id': lead_id,
            'plumber_id': plumber_id,
            'claimed_at': datetime.utcnow().isoformat(),
            'status': 'new',
            'notes': notes
        }
        
        claim = LeadClaim.create(claim_data)
        if not claim:
            # Refund the lead credit if claim creation fails
            plumber.add_lead_credits(1)
            logger.error(f"Failed to create lead claim for lead {lead_id} and plumber {plumber_id}")
            return {
                'success': False,
                'error': 'Failed to create lead claim'
            }
        
        # Update lead status to claimed if this is the first claim
        existing_claims = LeadClaim.get_by_lead(lead_id)
        if len(existing_claims) <= 1:  # Only this new claim exists
            Lead.update_status(lead_id, 'claimed')
        
        logger.info(f"Lead {lead_id} successfully claimed by plumber {plumber_id}")
        return {
            'success': True,
            'claim': claim
        }
        
    except Exception as e:
        logger.error(f"Error claiming lead {lead_id} for plumber {plumber_id}: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': 'An error occurred while claiming the lead'
        }


def get_available_leads_for_plumber(plumber_id, limit=10, offset=0):
    """
    Get leads available for a specific plumber based on location and services.
    
    Args:
        plumber_id: ID of the plumber
        limit: Maximum number of leads to return
        offset: Offset for pagination
        
    Returns:
        List of available leads
    """
    logger.info(f"Fetching available leads for plumber {plumber_id}")
    
    try:
        # Get plumber details
        plumber = Plumber.get_by_id(plumber_id)
        if not plumber:
            logger.warning(f"Plumber {plumber_id} not found when fetching leads")
            return []
            
        # Find leads within the plumber's service radius
        leads = Lead.find_by_location(
            latitude=plumber.latitude,
            longitude=plumber.longitude,
            radius_miles=plumber.service_radius,
            limit=limit
        )
        
        # Filter out leads that the plumber has already claimed
        claimed_lead_ids = set()
        plumber_claims = LeadClaim.get_by_plumber(plumber_id)
        for claim in plumber_claims:
            claimed_lead_ids.add(claim.lead_id)
        
        available_leads = [lead for lead in leads if lead.id not in claimed_lead_ids]
        
        # Apply pagination
        paginated_leads = available_leads[offset:offset + limit]
        
        logger.info(f"Found {len(paginated_leads)} available leads for plumber {plumber_id}")
        return paginated_leads
        
    except Exception as e:
        logger.error(f"Error fetching leads for plumber {plumber_id}: {str(e)}", exc_info=True)
        return []


def get_lead_statistics(start_date=None, end_date=None, plumber_id=None):
    """
    Get statistics about leads for reporting.
    
    Args:
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
        plumber_id: Filter by plumber ID (optional)
        
    Returns:
        Dictionary with statistics
    """
    # This would typically be a complex database query
    # For simplicity, this is a placeholder that would need to be implemented
    # with proper database aggregation queries
    
    # Example return structure:
    return {
        'total_leads': 0,
        'claimed_leads': 0,
        'completed_jobs': 0,
        'average_response_time': 0,
        'geographic_distribution': {},
        'service_type_distribution': {}
    }

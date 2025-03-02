# app/services/mock/geocoding_service.py
"""
Mock geocoding service for local development.
This avoids making actual API calls during development.
"""
import random
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

# Pre-defined coordinates for various US cities to get realistic test data
CITY_COORDINATES = {
    'New York': {'lat': 40.7128, 'lng': -74.0060},
    'Los Angeles': {'lat': 34.0522, 'lng': -118.2437},
    'Chicago': {'lat': 41.8781, 'lng': -87.6298},
    'Houston': {'lat': 29.7604, 'lng': -95.3698},
    'Phoenix': {'lat': 33.4484, 'lng': -112.0740},
    'Philadelphia': {'lat': 39.9526, 'lng': -75.1652},
    'San Antonio': {'lat': 29.4241, 'lng': -98.4936},
    'San Diego': {'lat': 32.7157, 'lng': -117.1611},
    'Dallas': {'lat': 32.7767, 'lng': -96.7970},
    'San Jose': {'lat': 37.3382, 'lng': -121.8863},
    'Austin': {'lat': 30.2672, 'lng': -97.7431},
    'Jacksonville': {'lat': 30.3322, 'lng': -81.6557},
    'Fort Worth': {'lat': 32.7555, 'lng': -97.3308},
    'Columbus': {'lat': 39.9612, 'lng': -82.9988},
    'Indianapolis': {'lat': 39.7684, 'lng': -86.1581},
    'Charlotte': {'lat': 35.2271, 'lng': -80.8431},
    'San Francisco': {'lat': 37.7749, 'lng': -122.4194},
    'Seattle': {'lat': 47.6062, 'lng': -122.3321},
    'Denver': {'lat': 39.7392, 'lng': -104.9903},
    'Washington': {'lat': 38.9072, 'lng': -77.0369}
}

# State abbreviations for default mapping
STATE_ABBR = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

def mock_geocode(address: str, city: str, state: str, zip_code: str) -> Tuple[float, float]:
    """
    Mock geocoding function that returns consistent but realistic coordinates
    based on city and state, with small random variations to simulate different addresses.
    
    Args:
        address: Street address
        city: City name
        state: State or province code (2-letter)
        zip_code: Postal code
        
    Returns:
        Tuple of (latitude, longitude)
    """
    logger.info(f"MOCK: Geocoding address {address}, {city}, {state} {zip_code}")
    
    # Look up the base coordinates for this city, or use a random city if not found
    state_name = STATE_ABBR.get(state.upper(), state)
    city_key = city
    
    if city_key in CITY_COORDINATES:
        base_coord = CITY_COORDINATES[city_key]
    else:
        # If city not found, pick a random city from our list
        random_city = random.choice(list(CITY_COORDINATES.keys()))
        base_coord = CITY_COORDINATES[random_city]
        logger.info(f"MOCK: Unknown city '{city}', using coordinates from '{random_city}' instead")
    
    # Add small random variations to simulate different addresses within the same city
    # Approximately within a few miles
    lat_variation = (random.random() - 0.5) * 0.05
    lng_variation = (random.random() - 0.5) * 0.05
    
    latitude = base_coord['lat'] + lat_variation
    longitude = base_coord['lng'] + lng_variation
    
    logger.info(f"MOCK: Geocoded to ({latitude}, {longitude})")
    return latitude, longitude


# app/services/mock/email_service.py
"""
Mock email service for local development.
This logs emails instead of actually sending them.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def mock_send_email(
    recipient: str, 
    subject: str, 
    body: str, 
    html_body: Optional[str] = None, 
    sender: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> bool:
    """
    Mock email sending that logs the email details instead of sending.
    
    Args:
        recipient: Email address of the recipient
        subject: Email subject
        body: Plain text email body
        html_body: HTML email body (optional)
        sender: Sender email address (optional)
        cc: List of CC recipients (optional)
        bcc: List of BCC recipients (optional)
        attachments: List of attachment dictionaries (optional)
        
    Returns:
        True to simulate successful sending
    """
    logger.info("=" * 80)
    logger.info("MOCK EMAIL")
    logger.info(f"To: {recipient}")
    if cc:
        logger.info(f"CC: {', '.join(cc)}")
    if bcc:
        logger.info(f"BCC: {', '.join(bcc)}")
    if sender:
        logger.info(f"From: {sender}")
    logger.info(f"Subject: {subject}")
    logger.info("-" * 40)
    logger.info(f"Body:\n{body}")
    if html_body:
        logger.info("-" * 40)
        logger.info(f"HTML Body:\n{html_body[:500]}...")
    if attachments:
        logger.info("-" * 40)
        logger.info(f"Attachments: {len(attachments)}")
        for i, attachment in enumerate(attachments):
            logger.info(f"  {i+1}. {attachment.get('filename', 'Unnamed')}")
    logger.info("=" * 80)
    return True


# app/services/mock/sms_service.py
"""
Mock SMS service for local development.
This logs SMS messages instead of actually sending them.
"""
import logging

logger = logging.getLogger(__name__)

def mock_send_sms(to_number: str, message: str, from_number: str = None) -> bool:
    """
    Mock SMS sending that logs the message instead of sending.
    
    Args:
        to_number: Recipient's phone number
        message: SMS text message
        from_number: Sender's phone number (optional)
        
    Returns:
        True to simulate successful sending
    """
    logger.info("=" * 80)
    logger.info("MOCK SMS")
    logger.info(f"To: {to_number}")
    if from_number:
        logger.info(f"From: {from_number}")
    logger.info("-" * 40)
    logger.info(f"Message:\n{message}")
    logger.info("=" * 80)
    return True


# app/services/mock/__init__.py
"""
Initialization for mock services
"""

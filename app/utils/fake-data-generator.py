# app/utils/fake_data.py
"""
Utility to generate fake data for development and testing.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from faker import Faker
from app.models.lead import Lead
from app.models.plumber import Plumber
from app.models.lead_claim import LeadClaim
from app.services.auth_service import signup
from app.services.mock.geocoding_service import CITY_COORDINATES, STATE_ABBR

# Initialize faker
fake = Faker('en_US')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PLUMBING_SERVICES = [
    'emergency', 'leak', 'drain', 'toilet', 'faucet', 'sink', 'disposal', 
    'water_heater', 'sewer', 'repiping', 'gas_line', 'backflow', 'waterproofing', 
    'sump_pump', 'commercial', 'inspection', 'maintenance', 'renovation', 'other'
]

URGENCY_OPTIONS = [
    'emergency', 'today', 'tomorrow', 'this_week', 'next_week', 'flexible'
]

LEAD_STATUSES = ['new', 'matched', 'claimed', 'completed']
CLAIM_STATUSES = ['new', 'contacted', 'completed', 'abandoned']
CONTACT_STATUSES = ['attempted', 'reached', 'no-answer', 'scheduled']


def generate_fake_users(count: int = 10) -> List[Dict[str, Any]]:
    """Generate fake users for development."""
    users = []
    
    logger.info(f"Generating {count} fake users...")
    
    # Create admin user
    admin_user = signup(
        'admin@example.com', 
        'admin123', 
        {'role': 'admin', 'name': 'Admin User'}
    )
    users.append({
        'id': admin_user.id,
        'email': 'admin@example.com',
        'role': 'admin'
    })
    logger.info(f"Created admin user: admin@example.com / admin123")
    
    # Create regular plumber users
    for i in range(count):
        company_name = fake.company()
        email = f"plumber{i+1}@example.com"
        password = "password123"
        
        user = signup(
            email, 
            password, 
            {'role': 'plumber', 'company_name': company_name}
        )
        
        if user:
            users.append({
                'id': user.id,
                'email': email,
                'role': 'plumber',
                'company_name': company_name
            })
            logger.info(f"Created plumber user: {email} / {password}")
    
    return users


def generate_fake_plumbers(users: List[Dict[str, Any]], count: int = 10) -> List[Dict[str, Any]]:
    """Generate fake plumber profiles for development."""
    plumbers = []
    
    logger.info(f"Generating {count} fake plumber profiles...")
    
    # Filter plumber users
    plumber_users = [user for user in users if user.get('role') == 'plumber']
    
    # City selection for reasonable distribution
    cities = list(CITY_COORDINATES.keys())
    
    for i, user in enumerate(plumber_users):
        if i >= count:
            break
            
        # Select a random city and state
        city = random.choice(cities)
        coordinates = CITY_COORDINATES[city]
        state_code = random.choice(list(STATE_ABBR.keys()))
        state_name = STATE_ABBR[state_code]
        
        # Generate services offered (3-10 random services)
        service_count = random.randint(3, 10)
        services_offered = random.sample(PLUMBING_SERVICES, service_count)
        
        # Generate random service radius (15-50 miles)
        service_radius = random.randint(15, 50)
        
        plumber_data = {
            'user_id': user['id'],
            'company_name': user['company_name'],
            'contact_name': fake.name(),
            'email': user['email'],
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': city,
            'state': state_code,
            'zip_code': fake.zipcode(),
            'service_radius': service_radius,
            'services_offered': services_offered,
            'license_number': f"{state_code}-{fake.numerify('######')}",
            'is_insured': random.choice([True, True, True, False]),  # 75% insured
            'latitude': coordinates['lat'] + (random.random() - 0.5) * 0.05,
            'longitude': coordinates['lng'] + (random.random() - 0.5) * 0.05,
            'is_active': True,
            'subscription_status': random.choice(['active', 'active', 'active', 'inactive']),  # 75% active
            'stripe_customer_id': f"cus_{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=14))}",
            'stripe_subscription_id': f"sub_{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=14))}",
            'lead_credits': random.randint(0, 50),
            'created_at': datetime.now() - timedelta(days=random.randint(1, 180))
        }
        
        # Create plumber profile
        plumber = Plumber.create(plumber_data)
        
        if plumber:
            plumbers.append(plumber)
            logger.info(f"Created plumber profile for {user['email']} in {city}, {state_code}")
    
    return plumbers


def generate_fake_leads(count: int = 50) -> List[Dict[str, Any]]:
    """Generate fake customer leads for development."""
    leads = []
    
    logger.info(f"Generating {count} fake customer leads...")
    
    # City selection for reasonable distribution
    cities = list(CITY_COORDINATES.keys())
    
    for i in range(count):
        # Select a random city and state
        city = random.choice(cities)
        coordinates = CITY_COORDINATES[city]
        state_code = random.choice(list(STATE_ABBR.keys()))
        
        # Generate services needed (1-3 random services)
        service_count = random.randint(1, 3)
        service_needed = random.sample(PLUMBING_SERVICES, service_count)
        
        # Generate random status weighted toward new
        status_weights = [0.6, 0.2, 0.15, 0.05]  # new, matched, claimed, completed
        status = random.choices(LEAD_STATUSES, weights=status_weights, k=1)[0]
        
        # Generate random date in the past 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Generate reference code
        reference_code = f"PL-{fake.numerify('######')}"
        
        lead_data = {
            'customer_name': fake.name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': city,
            'state': state_code,
            'zip_code': fake.zipcode(),
            'problem_description': fake.paragraph(nb_sentences=3),
            'service_needed': service_needed,
            'urgency': random.choice(URGENCY_OPTIONS),
            'latitude': coordinates['lat'] + (random.random() - 0.5) * 0.05,
            'longitude': coordinates['lng'] + (random.random() - 0.5) * 0.05,
            'created_at': created_at.isoformat(),
            'status': status,
            'reference_code': reference_code
        }
        
        # Create lead
        lead = Lead.create(lead_data)
        
        if lead:
            leads.append(lead)
            logger.info(f"Created lead #{i+1}: {reference_code} in {city}, {state_code} ({status})")
    
    return leads


def generate_fake_claims(plumbers: List[Dict[str, Any]], leads: List[Dict[str, Any]], count: int = 30) -> List[Dict[str, Any]]:
    """Generate fake lead claims for development."""
    claims = []
    
    logger.info(f"Generating up to {count} fake lead claims...")
    
    # Filter leads that can be claimed (new or matched)
    claimable_leads = [lead for lead in leads if lead.status in ['new', 'matched', 'claimed']]
    
    # Filter active plumbers
    active_plumbers = [plumber for plumber in plumbers if plumber.subscription_status == 'active' and plumber.lead_credits > 0]
    
    if not claimable_leads or not active_plumbers:
        logger.warning("No claimable leads or active plumbers available for generating claims")
        return claims
    
    # Generate claims (up to the requested count or available leads)
    actual_count = min(count, len(claimable_leads))
    
    for i in range(actual_count):
        # Select a random lead
        lead = random.choice(claimable_leads)
        
        # Select a random plumber (prioritize plumbers in the same city)
        local_plumbers = [p for p in active_plumbers if p.city == lead.city]
        if local_plumbers:
            plumber = random.choice(local_plumbers)
        else:
            plumber = random.choice(active_plumbers)
        
        # Use a lead credit
        if plumber.lead_credits <= 0:
            continue
            
        plumber.use_lead_credit()
        
        # Determine claim status based on lead status
        if lead.status == 'completed':
            status = 'completed'
        else:
            status_weights = [0.4, 0.3, 0.2, 0.1]  # new, contacted, completed, abandoned
            status = random.choices(CLAIM_STATUSES, weights=status_weights, k=1)[0]
        
        # Set contact status if applicable
        contact_status = None
        if status in ['contacted', 'completed']:
            contact_status = random.choice(CONTACT_STATUSES)
        
        # Set claim date (after lead creation but before now)
        lead_date = datetime.fromisoformat(lead.created_at) if isinstance(lead.created_at, str) else lead.created_at
        max_days_since = (datetime.now() - lead_date).days
        if max_days_since <= 0:
            max_days_since = 1
        days_after = random.randint(0, max_days_since)
        claimed_at = lead_date + timedelta(days=days_after, hours=random.randint(0, 23))
        
        claim_data = {
            'lead_id': lead.id,
            'plumber_id': plumber.id,
            'claimed_at': claimed_at.isoformat(),
            'status': status,
            'contact_status': contact_status,
            'notes': fake.paragraph(nb_sentences=2) if random.random() > 0.3 else None
        }
        
        # Create claim
        claim = LeadClaim.create(claim_data)
        
        if claim:
            claims.append(claim)
            logger.info(f"Created claim: Lead '{lead.reference_code}' claimed by '{plumber.company_name}' ({status})")
            
            # Update lead status if this is the first claim
            if lead.status == 'new':
                Lead.update_status(lead.id, 'claimed')
                lead.status = 'claimed'
                
            # Mark lead as completed if claim is completed
            if status == 'completed' and lead.status != 'completed':
                Lead.update_status(lead.id, 'completed')
                lead.status = 'completed'
            
            # Remove lead from claimable_leads if it's been claimed by this plumber
            if lead in claimable_leads:
                claimable_leads.remove(lead)
    
    return claims


def generate_fake_data(user_count: int = 10, plumber_count: int = 10, lead_count: int = 50, claim_count: int = 30):
    """
    Generate complete fake dataset for development.
    
    Args:
        user_count: Number of users to generate
        plumber_count: Number of plumber profiles to generate
        lead_count: Number of customer leads to generate
        claim_count: Number of lead claims to generate
    """
    logger.info("Generating fake data for development...")
    
    # Generate in proper order to maintain relationships
    users = generate_fake_users(user_count)
    plumbers = generate_fake_plumbers(users, plumber_count)
    leads = generate_fake_leads(lead_count)
    claims = generate_fake_claims(plumbers, leads, claim_count)
    
    logger.info("Fake data generation complete!")
    logger.info(f"Generated {len(users)} users, {len(plumbers)} plumber profiles, {len(leads)} leads, and {len(claims)} claims")
    
    # Show login credentials for convenience
    logger.info("\nTest login credentials:")
    logger.info("  Admin: admin@example.com / admin123")
    for i in range(min(3, len(users) - 1)):  # Show first 3 plumber accounts
        logger.info(f"  Plumber: plumber{i+1}@example.com / password123")


if __name__ == "__main__":
    generate_fake_data()

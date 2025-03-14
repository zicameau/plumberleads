#!/usr/bin/env python
# app/utils/fake_data.py
"""
Utility to generate fake data for development and testing.
"""
import random
import uuid
from datetime import datetime, timedelta
import logging

from faker import Faker
from flask import current_app
from sqlalchemy import text

from app.models.base import db, User, Plumber, Lead, LeadClaim, Setting
from app.models.base import UserRole, LeadStatus, ClaimStatus, ContactStatus, SubscriptionStatus, ServiceType, UrgencyType

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

CITIES = [
    ('New York', 'NY', 40.7128, -74.0060),
    ('Los Angeles', 'CA', 34.0522, -118.2437),
    ('Chicago', 'IL', 41.8781, -87.6298),
    ('Houston', 'TX', 29.7604, -95.3698),
    ('Phoenix', 'AZ', 33.4484, -112.0740),
    ('Philadelphia', 'PA', 39.9526, -75.1652),
    ('San Antonio', 'TX', 29.4241, -98.4936),
    ('San Diego', 'CA', 32.7157, -117.1611),
    ('Dallas', 'TX', 32.7767, -96.7970),
    ('San Jose', 'CA', 37.3382, -121.8863)
]

def generate_fake_users(count=10):
    """Generate fake users for development."""
    users = []
    
    logger.info(f"Generating {count} fake users...")
    
    # Create admin user if it doesn't exist
    admin_user = db.session.query(User).filter_by(email='admin@example.com').first()
    if not admin_user:
        admin_user = User(
            id=str(uuid.uuid4()),
            email='admin@example.com',
            role=UserRole.admin
        )
        db.session.add(admin_user)
        db.session.commit()
        logger.info(f"Created admin user: admin@example.com / admin123")
    
    # Create regular plumber users
    for i in range(count):
        company_name = fake.company()
        email = f"plumber{i+1}@example.com"
        
        # Check if user already exists
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                role=UserRole.plumber
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created plumber user: {email}")
        
        users.append(user)
    
    return users

def generate_fake_plumbers(users, count=10):
    """Generate fake plumber profiles for development."""
    plumbers = []
    
    logger.info(f"Generating {count} fake plumber profiles...")
    
    # Filter plumber users
    plumber_users = [user for user in users if user.role == UserRole.plumber]
    
    for i, user in enumerate(plumber_users):
        if i >= count:
            break
            
        # Select a random city and state
        city, state, lat, lng = random.choice(CITIES)
        
        # Add some randomness to coordinates
        latitude = lat + (random.random() - 0.5) * 0.05
        longitude = lng + (random.random() - 0.5) * 0.05
        
        # Generate services offered (3-10 random services)
        service_count = random.randint(3, 10)
        services_offered = random.sample(PLUMBING_SERVICES, service_count)
        
        # Generate random service radius (15-50 miles)
        service_radius = random.randint(15, 50)
        
        # Check if plumber already exists
        plumber = db.session.query(Plumber).filter_by(user_id=user.id).first()
        if not plumber:
            plumber = Plumber(
                id=str(uuid.uuid4()),
                user_id=user.id,
                company_name=fake.company(),
                contact_name=fake.name(),
                email=user.email,
                phone=fake.phone_number(),
                address=fake.street_address(),
                city=city,
                state=state,
                zip_code=fake.zipcode(),
                service_radius=service_radius,
                services_offered=services_offered,
                license_number=f"{state}-{fake.numerify('######')}",
                is_insured=random.choice([True, True, True, False]),  # 75% insured
                latitude=latitude,
                longitude=longitude,
                is_active=True,
                subscription_status=random.choice([
                    SubscriptionStatus.active, 
                    SubscriptionStatus.active, 
                    SubscriptionStatus.active, 
                    SubscriptionStatus.inactive
                ]),  # 75% active
                stripe_customer_id=f"cus_{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=14))}",
                stripe_subscription_id=f"sub_{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=14))}",
                lead_credits=random.randint(0, 50),
                created_at=datetime.now() - timedelta(days=random.randint(1, 180))
            )
            db.session.add(plumber)
            db.session.commit()
            logger.info(f"Created plumber profile for {user.email} in {city}, {state}")
        
        plumbers.append(plumber)
    
    return plumbers

def generate_fake_leads(count=30):
    """Generate fake customer leads for development."""
    leads = []
    
    logger.info(f"Generating {count} fake customer leads...")
    
    for i in range(count):
        # Select a random city and state
        city, state, lat, lng = random.choice(CITIES)
        
        # Add some randomness to coordinates
        latitude = lat + (random.random() - 0.5) * 0.05
        longitude = lng + (random.random() - 0.5) * 0.05
        
        # Generate services needed (1-3 random services)
        service_count = random.randint(1, 3)
        service_needed = random.sample(PLUMBING_SERVICES, service_count)
        
        # Generate random status weighted toward new
        status_weights = [0.6, 0.2, 0.15, 0.05]  # new, matched, claimed, completed
        status = random.choices([s.value for s in LeadStatus], weights=status_weights, k=1)[0]
        
        # Generate random date in the past 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Generate reference code
        reference_code = f"PL-{fake.numerify('######')}"
        
        lead = Lead(
            id=str(uuid.uuid4()),
            customer_name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.street_address(),
            city=city,
            state=state,
            zip_code=fake.zipcode(),
            problem_description=fake.paragraph(nb_sentences=3),
            service_needed=service_needed,
            urgency=UrgencyType(random.choice(URGENCY_OPTIONS)),
            latitude=latitude,
            longitude=longitude,
            status=LeadStatus(status),
            reference_code=reference_code,
            created_at=created_at
        )
        
        db.session.add(lead)
        db.session.commit()
        logger.info(f"Created lead #{i+1}: {reference_code} in {city}, {state} ({status})")
        leads.append(lead)
    
    return leads

def generate_fake_claims(plumbers, leads, count=20):
    """Generate fake lead claims for development."""
    claims = []
    
    logger.info(f"Generating up to {count} fake lead claims...")
    
    # Filter leads that can be claimed
    claimable_leads = [lead for lead in leads if lead.status in [LeadStatus.new, LeadStatus.matched, LeadStatus.claimed]]
    
    # Filter active plumbers
    active_plumbers = [plumber for plumber in plumbers 
                      if plumber.subscription_status == SubscriptionStatus.active and plumber.lead_credits > 0]
    
    if not claimable_leads or not active_plumbers:
        logger.warning("No claimable leads or active plumbers available for generating claims")
        return claims
    
    # Generate claims (up to the requested count or available leads)
    actual_count = min(count, len(claimable_leads))
    
    for i in range(actual_count):
        # Select a random lead
        lead = random.choice(claimable_leads)
        claimable_leads.remove(lead)  # Don't claim the same lead twice
        
        # Select a random plumber (prioritize plumbers in the same city)
        local_plumbers = [p for p in active_plumbers if p.city == lead.city]
        if local_plumbers:
            plumber = random.choice(local_plumbers)
        else:
            plumber = random.choice(active_plumbers)
        
        # Use a lead credit
        if plumber.lead_credits <= 0:
            continue
            
        plumber.lead_credits -= 1
        
        # Determine claim status based on lead status
        if lead.status == LeadStatus.completed:
            status = ClaimStatus.completed
        else:
            status_weights = [0.4, 0.3, 0.2, 0.1]  # new, contacted, completed, abandoned
            status = random.choices(list(ClaimStatus), weights=status_weights, k=1)[0]
        
        # Set contact status if applicable
        contact_status = None
        if status in [ClaimStatus.contacted, ClaimStatus.completed]:
            contact_status = random.choice(list(ContactStatus))
        
        # Set claim date
        days_after = random.randint(0, 5)
        claimed_at = lead.created_at + timedelta(days=days_after, hours=random.randint(0, 23))
        
        claim = LeadClaim(
            id=str(uuid.uuid4()),
            lead_id=lead.id,
            plumber_id=plumber.id,
            claimed_at=claimed_at,
            status=status,
            contact_status=contact_status,
            notes=fake.paragraph(nb_sentences=2) if random.random() > 0.3 else None
        )
        
        db.session.add(claim)
        db.session.commit()
        
        logger.info(f"Created claim: Lead '{lead.reference_code}' claimed by '{plumber.company_name}' ({status.value})")
        claims.append(claim)
        
        # Update lead status if this is the first claim
        if lead.status == LeadStatus.new:
            lead.status = LeadStatus.claimed
            db.session.commit()
        
        # Mark lead as completed if claim is completed
        if status == ClaimStatus.completed and lead.status != LeadStatus.completed:
            lead.status = LeadStatus.completed
            db.session.commit()
    
    return claims

def generate_fake_data(user_count=10, plumber_count=10, lead_count=30, claim_count=20):
    """
    Generate complete fake dataset for development.
    
    Args:
        user_count: Number of users to generate
        plumber_count: Number of plumber profiles to generate
        lead_count: Number of customer leads to generate
        claim_count: Number of lead claims to generate
    """
    logger.info("Generating fake data for development...")
    
    with current_app.app_context():
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
    # This only runs when script is executed directly, not when imported
    from flask import Flask
    from app import create_app
    
    app = create_app('development')
    with app.app_context():
        generate_fake_data()
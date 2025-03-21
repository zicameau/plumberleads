#!/usr/bin/env python
import os
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.user import User
from app.models.lead import Lead
from app.models.payment import Payment
from app.models.lead_history import LeadHistory
from config import config

# Load environment variables
load_dotenv()

def create_sample_users():
    """Create sample users for testing."""
    print("Creating sample users...")
    
    # Admin user
    admin = User(
        email='admin@plumberleads.com',
        full_name='Admin User',
        company_name='PlumberLeads',
        phone='555-123-4567',
        is_active=True,
        is_admin=True,
        is_verified=True,
        service_areas=json.dumps([]),
        service_types=json.dumps([]),
        # Add address fields for admin
        address='123 Admin St',
        city='San Francisco',
        state='CA',
        zip_code='94105',
        latitude=37.7749,
        longitude=-122.4194,
        service_radius=25,
        # Add required fields
        business_description='Administrative account for PlumberLeads platform',
        license_number='ADMIN-001',
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    admin.password_hash = generate_password_hash('adminpassword')
    db.session.add(admin)
    
    # Regular plumbers with addresses
    plumbers = [
        {
            'email': 'john@example.com',
            'password': 'password123',
            'full_name': 'John Smith',
            'company_name': 'Smith Plumbing',
            'phone': '555-234-5678',
            'address': '456 Main St',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'service_radius': 30,
            'service_areas': ['New York, NY', 'Brooklyn, NY', 'Queens, NY'],
            'service_types': ['Residential Plumbing', 'Emergency Repairs', 'Pipe Repair'],
            'business_description': 'Professional plumbing services for residential and commercial properties',
            'license_number': 'NY-12345'
        },
        {
            'email': 'sarah@example.com',
            'password': 'password123',
            'full_name': 'Sarah Johnson',
            'company_name': 'Johnson Plumbing Services',
            'phone': '555-345-6789',
            'address': '789 Ocean Ave',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip_code': '90001',
            'latitude': 34.0522,
            'longitude': -118.2437,
            'service_radius': 25,
            'service_areas': ['Los Angeles, CA', 'Long Beach, CA', 'Pasadena, CA'],
            'service_types': ['Commercial Plumbing', 'Water Heater Installation', 'Drain Cleaning'],
            'business_description': 'Expert plumbing solutions for commercial and industrial clients',
            'license_number': 'CA-67890'
        },
        {
            'email': 'mike@example.com',
            'password': 'password123',
            'full_name': 'Mike Wilson',
            'company_name': 'Wilson Plumbing & Heating',
            'phone': '555-456-7890',
            'address': '321 Lake St',
            'city': 'Chicago',
            'state': 'IL',
            'zip_code': '60601',
            'latitude': 41.8781,
            'longitude': -87.6298,
            'service_radius': 35,
            'service_areas': ['Chicago, IL', 'Evanston, IL', 'Oak Park, IL'],
            'service_types': ['Residential Plumbing', 'Commercial Plumbing', 'Gas Line Services'],
            'business_description': 'Full-service plumbing and heating solutions for all your needs',
            'license_number': 'IL-45678'
        }
    ]
    
    for p in plumbers:
        plumber = User(
            email=p['email'],
            full_name=p['full_name'],
            company_name=p['company_name'],
            phone=p['phone'],
            is_active=True,
            is_admin=False,
            is_verified=True,
            # Add address fields
            address=p['address'],
            city=p['city'],
            state=p['state'],
            zip_code=p['zip_code'],
            latitude=p['latitude'],
            longitude=p['longitude'],
            service_radius=p['service_radius'],
            service_areas=json.dumps(p['service_areas']),
            service_types=json.dumps(p['service_types']),
            # Add required fields
            business_description=p['business_description'],
            license_number=p['license_number'],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
        )
        plumber.password_hash = generate_password_hash(p['password'])
        db.session.add(plumber)
    
    db.session.commit()
    print("Sample users created!")

def create_sample_leads():
    """Create sample leads for testing."""
    print("Creating sample leads...")
    
    service_types = [
        'Residential Plumbing',
        'Commercial Plumbing',
        'Emergency Repairs',
        'Water Heater Installation',
        'Pipe Repair',
        'Drain Cleaning',
        'Sewer Line Repair',
        'Fixture Installation',
        'Gas Line Services',
        'Water Treatment'
    ]
    
    urgency_levels = ['low', 'medium', 'high']
    
    locations = [
        # San Jose locations
        {
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95110',
            'latitude': 37.3382,
            'longitude': -121.8863
        },
        {
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95123',
            'latitude': 37.2469,
            'longitude': -121.8310
        },
        {
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95125',
            'latitude': 37.2987,
            'longitude': -121.9012
        },
        {
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95128',
            'latitude': 37.3219,
            'longitude': -121.9462
        },
        {
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95131',
            'latitude': 37.3871,
            'longitude': -121.8897
        },
        # Other cities
        {
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001',
            'latitude': 40.7128,
            'longitude': -74.0060
        },
        {
            'city': 'Los Angeles',
            'state': 'CA',
            'zip_code': '90001',
            'latitude': 34.0522,
            'longitude': -118.2437
        },
        {
            'city': 'Chicago',
            'state': 'IL',
            'zip_code': '60601',
            'latitude': 41.8781,
            'longitude': -87.6298
        },
        {
            'city': 'Houston',
            'state': 'TX',
            'zip_code': '77001',
            'latitude': 29.7604,
            'longitude': -95.3698
        },
        {
            'city': 'Phoenix',
            'state': 'AZ',
            'zip_code': '85001',
            'latitude': 33.4484,
            'longitude': -112.0740
        }
    ]
    
    lead_titles = [
        # San Jose specific leads
        'Leaking water heater in downtown San Jose',
        'Clogged kitchen sink in Willow Glen',
        'Burst pipe emergency in Almaden Valley',
        'New bathroom renovation in Rose Garden',
        'Commercial kitchen plumbing issue in downtown',
        'Sewer line backup in Cambrian Park',
        'Gas line installation for new stove in Naglee Park',
        'Water filtration system installation in Evergreen',
        'Pipe leak under sink in Santa Teresa',
        'Shower drain clogged in West San Jose',
        'Garbage disposal not working in Alum Rock',
        'Low water pressure issue in Berryessa',
        'Water softener installation in North San Jose',
        'Toilet constantly running in Japantown',
        'Emergency plumbing repair in Downtown',
        # General leads
        'Need plumber for leaking faucet',
        'Toilet constantly running',
        'Water heater replacement needed',
        'Clogged drain in kitchen',
        'Burst pipe emergency',
        'New bathroom fixture installation',
        'Commercial kitchen plumbing issue',
        'Sewer line backup',
        'Gas line installation for stove',
        'Water filtration system installation',
        'Pipe leak under sink',
        'Shower drain clogged',
        'Garbage disposal not working',
        'Low water pressure issue',
        'Water softener installation'
    ]
    
    # Create 30 sample leads (increased to include more San Jose leads)
    for i in range(30):
        location = random.choice(locations)
        service_type = random.choice(service_types)
        urgency = random.choice(urgency_levels)
        days_ago = random.randint(0, 14)
        
        # Add some random variation to coordinates within the city
        lat_variation = random.uniform(-0.05, 0.05)  # Reduced variation for more accurate locations
        lng_variation = random.uniform(-0.05, 0.05)
        
        # Generate San Jose specific details if the location is San Jose
        if location['city'] == 'San Jose':
            customer_name = f"San Jose Customer {i+1}"
            customer_email = f"sjcustomer{i+1}@example.com"
            customer_phone = f"408-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            address = f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak St', 'Maple Ave', 'Park Ave', 'Market St'])}"
            price = random.randint(100, 500)  # Higher price range for San Jose
        else:
            customer_name = f"Customer {i+1}"
            customer_email = f"customer{i+1}@example.com"
            customer_phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            address = f"{random.randint(100, 9999)} Main St"
            price = random.randint(50, 300)
        
        lead = Lead(
            title=random.choice(lead_titles),
            description=f"Customer needs assistance with {service_type.lower()}. This is a {urgency} priority request.",
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            address=address,
            city=location['city'],
            state=location['state'],
            zip_code=location['zip_code'],
            latitude=location['latitude'] + lat_variation,
            longitude=location['longitude'] + lng_variation,
            service_type=service_type,
            service_details="Detailed information about the service request would go here.",
            urgency=urgency,
            price=price,
            status='available',
            source='website',
            created_at=datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
        )
        db.session.add(lead)
    
    # Create 5 claimed leads
    users = User.query.filter_by(is_admin=False).all()
    for i in range(5):
        plumber = random.choice(users)
        location = random.choice(locations)
        service_type = random.choice(service_types)
        urgency = random.choice(urgency_levels)
        days_ago = random.randint(3, 30)
        
        # Add some random variation to coordinates within the city
        lat_variation = random.uniform(-0.05, 0.05)
        lng_variation = random.uniform(-0.05, 0.05)
        
        # Generate San Jose specific details if the location is San Jose
        if location['city'] == 'San Jose':
            customer_name = f"San Jose Claimed Customer {i+1}"
            customer_email = f"sjclaimedcustomer{i+1}@example.com"
            customer_phone = f"408-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            address = f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak St', 'Maple Ave', 'Park Ave', 'Market St'])}"
            price = random.randint(100, 500)
        else:
            customer_name = f"Claimed Customer {i+1}"
            customer_email = f"claimedcustomer{i+1}@example.com"
            customer_phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            address = f"{random.randint(100, 9999)} Oak St"
            price = random.randint(50, 300)
        
        lead = Lead(
            title=random.choice(lead_titles),
            description=f"Customer needs assistance with {service_type.lower()}. This is a {urgency} priority request.",
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            address=address,
            city=location['city'],
            state=location['state'],
            zip_code=location['zip_code'],
            latitude=location['latitude'] + lat_variation,
            longitude=location['longitude'] + lng_variation,
            service_type=service_type,
            service_details="This lead has been claimed by a plumber.",
            urgency=urgency,
            price=price,
            status=random.choice(['in_progress', 'completed']),
            reserved_by_id=plumber.id,
            reserved_at=datetime.utcnow() - timedelta(days=random.randint(1, days_ago - 1)),
            notes="Plumber has contacted the customer and scheduled an appointment.",
            source='website',
            created_at=datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
        )
        db.session.add(lead)
    
    db.session.commit()
    print("Sample leads created!")

def create_sample_payments():
    """Create sample payments for testing."""
    print("Creating sample payments...")
    
    # Get claimed leads
    claimed_leads = Lead.query.filter_by(status='completed').all()
    
    for lead in claimed_leads:
        # Create a payment for each claimed lead
        payment = Payment(
            user_id=lead.reserved_by_id,
            lead_id=lead.id,
            amount=lead.price,
            currency='USD',
            payment_method='credit_card',
            payment_processor='stripe',
            processor_payment_id=f"pi_{random.randint(10000000, 99999999)}",
            status='completed',
            created_at=lead.reserved_at
        )
        db.session.add(payment)
    
    db.session.commit()
    print("Sample payments created!")

def create_sample_lead_history():
    """Create sample lead history entries for testing."""
    print("Creating sample lead history...")
    
    # Get all leads
    leads = Lead.query.all()
    
    for lead in leads:
        # Create history entries for status changes
        if lead.status != 'available':
            # Log reservation
            history_entry = LeadHistory(
                lead_id=lead.id,
                user_id=lead.reserved_by_id,
                field_name='status',
                old_value='available',
                new_value='reserved',
                change_type='status_change',
                created_at=lead.reserved_at
            )
            db.session.add(history_entry)
            
            # If lead is claimed, log the claim
            if lead.status == 'claimed':
                history_entry = LeadHistory(
                    lead_id=lead.id,
                    user_id=lead.reserved_by_id,
                    field_name='status',
                    old_value='reserved',
                    new_value='claimed',
                    change_type='status_change',
                    created_at=lead.reserved_at + timedelta(minutes=random.randint(1, 30))
                )
                db.session.add(history_entry)
        
        # Create history entries for price changes
        if random.random() < 0.3:  # 30% chance of price change
            old_price = lead.price
            new_price = old_price + random.randint(-50, 50)
            if new_price > 0:  # Ensure price doesn't go negative
                history_entry = LeadHistory(
                    lead_id=lead.id,
                    user_id=lead.reserved_by_id,
                    field_name='price',
                    old_value=str(old_price),
                    new_value=str(new_price),
                    change_type='price_update',
                    created_at=lead.created_at + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(history_entry)
    
    db.session.commit()
    print("Sample lead history created!")

def initialize_database(app=None):
    """Initialize the database with sample data."""
    if app is None:
        app = create_app()
        
    with app.app_context():
        create_sample_users()
        create_sample_leads()
        create_sample_payments()
        create_sample_lead_history()

if __name__ == '__main__':
    initialize_database() 
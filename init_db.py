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
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    admin.password_hash = generate_password_hash('adminpassword')
    db.session.add(admin)
    
    # Regular plumbers
    plumbers = [
        {
            'email': 'john@example.com',
            'password': 'password123',
            'full_name': 'John Smith',
            'company_name': 'Smith Plumbing',
            'phone': '555-234-5678',
            'service_areas': ['New York, NY', 'Brooklyn, NY', 'Queens, NY'],
            'service_types': ['Residential Plumbing', 'Emergency Repairs', 'Pipe Repair']
        },
        {
            'email': 'sarah@example.com',
            'password': 'password123',
            'full_name': 'Sarah Johnson',
            'company_name': 'Johnson Plumbing Services',
            'phone': '555-345-6789',
            'service_areas': ['Los Angeles, CA', 'Long Beach, CA', 'Pasadena, CA'],
            'service_types': ['Commercial Plumbing', 'Water Heater Installation', 'Drain Cleaning']
        },
        {
            'email': 'mike@example.com',
            'password': 'password123',
            'full_name': 'Mike Wilson',
            'company_name': 'Wilson Plumbing & Heating',
            'phone': '555-456-7890',
            'service_areas': ['Chicago, IL', 'Evanston, IL', 'Oak Park, IL'],
            'service_types': ['Residential Plumbing', 'Commercial Plumbing', 'Gas Line Services']
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
            service_areas=json.dumps(p['service_areas']),
            service_types=json.dumps(p['service_types']),
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
        {
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001'
        },
        {
            'city': 'Los Angeles',
            'state': 'CA',
            'zip_code': '90001'
        },
        {
            'city': 'Chicago',
            'state': 'IL',
            'zip_code': '60601'
        },
        {
            'city': 'Houston',
            'state': 'TX',
            'zip_code': '77001'
        },
        {
            'city': 'Phoenix',
            'state': 'AZ',
            'zip_code': '85001'
        }
    ]
    
    lead_titles = [
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
    
    # Create 20 sample leads
    for i in range(20):
        location = random.choice(locations)
        service_type = random.choice(service_types)
        urgency = random.choice(urgency_levels)
        days_ago = random.randint(0, 14)
        
        lead = Lead(
            title=random.choice(lead_titles),
            description=f"Customer needs assistance with {service_type.lower()}. This is a {urgency} priority request.",
            customer_name=f"Customer {i+1}",
            customer_email=f"customer{i+1}@example.com",
            customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            address=f"{random.randint(100, 9999)} Main St",
            city=location['city'],
            state=location['state'],
            zip_code=location['zip_code'],
            service_type=service_type,
            service_details="Detailed information about the service request would go here.",
            urgency=urgency,
            price=random.randint(50, 300),
            is_claimed=False,
            status='new',
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
        claimed_days_ago = random.randint(0, days_ago - 1)
        
        lead = Lead(
            title=random.choice(lead_titles),
            description=f"Customer needs assistance with {service_type.lower()}. This is a {urgency} priority request.",
            customer_name=f"Claimed Customer {i+1}",
            customer_email=f"claimedcustomer{i+1}@example.com",
            customer_phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            address=f"{random.randint(100, 9999)} Oak St",
            city=location['city'],
            state=location['state'],
            zip_code=location['zip_code'],
            service_type=service_type,
            service_details="This lead has been claimed by a plumber.",
            urgency=urgency,
            price=random.randint(50, 300),
            is_claimed=True,
            claimed_at=datetime.utcnow() - timedelta(days=claimed_days_ago),
            plumber_id=plumber.id,
            status=random.choice(['in_progress', 'completed']),
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
    claimed_leads = Lead.query.filter_by(is_claimed=True).all()
    
    for lead in claimed_leads:
        # Create a payment for each claimed lead
        payment = Payment(
            user_id=lead.plumber_id,
            lead_id=lead.id,
            amount=lead.price,
            currency='USD',
            payment_method='credit_card',
            payment_processor='stripe',
            processor_payment_id=f"pi_{random.randint(10000000, 99999999)}",
            status='completed',
            created_at=lead.claimed_at
        )
        db.session.add(payment)
    
    db.session.commit()
    print("Sample payments created!")

def initialize_database():
    """Initialize the database with sample data."""
    with app.app_context():
        print("Initializing database...")
        db.create_all()
        
        # Only create sample data if the database is empty
        if User.query.count() == 0:
            create_sample_users()
            create_sample_leads()
            create_sample_payments()
            print("Database initialized with sample data!")
        else:
            print("Database already contains data. Skipping sample data creation.")

if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config[env])
    initialize_database() 
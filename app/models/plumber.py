from app.models.base import BaseModel
from app.services.supabase import get_supabase
from datetime import datetime
import uuid
import logging
import json

# Get the database logger
logger = logging.getLogger('database')

class Plumber(BaseModel):
    """
    Plumber model for service providers.
    Maps to the 'plumbers' table in Supabase.
    """
    TABLE_NAME = 'plumbers'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.company_name = kwargs.get('company_name')
        self.contact_name = kwargs.get('contact_name')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')
        self.address = kwargs.get('address')
        self.city = kwargs.get('city')
        self.state = kwargs.get('state')
        self.zip_code = kwargs.get('zip_code')
        self.service_radius = kwargs.get('service_radius', 25)
        self.services_offered = kwargs.get('services_offered', [])
        self.license_number = kwargs.get('license_number')
        self.is_insured = kwargs.get('is_insured', False)
        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')
        self.is_active = kwargs.get('is_active', True)
        self.subscription_status = kwargs.get('subscription_status', 'inactive')
        self.stripe_customer_id = kwargs.get('stripe_customer_id')
        self.stripe_subscription_id = kwargs.get('stripe_subscription_id')
        self.lead_credits = kwargs.get('lead_credits', 0)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @classmethod
    def create(cls, plumber_data):
        """Create a new plumber profile in Supabase."""
        try:
            data = {
                'user_id': plumber_data['user_id'],
                'company_name': plumber_data['company_name'],
                'contact_name': plumber_data.get('contact_name'),
                'phone': plumber_data.get('phone'),
                'address': plumber_data.get('address'),
                'city': plumber_data.get('city'),
                'state': plumber_data.get('state'),
                'zip_code': plumber_data.get('zip_code'),
                'service_radius': plumber_data.get('service_radius', 25),
                'services_offered': plumber_data.get('services_offered', []),
                'license_number': plumber_data.get('license_number'),
                'is_insured': plumber_data.get('is_insured', False),
                'latitude': plumber_data.get('latitude'),
                'longitude': plumber_data.get('longitude'),
                'is_active': plumber_data.get('is_active', True),
                'subscription_status': plumber_data.get('subscription_status', 'inactive'),
                'stripe_customer_id': plumber_data.get('stripe_customer_id'),
                'stripe_subscription_id': plumber_data.get('stripe_subscription_id'),
                'lead_credits': plumber_data.get('lead_credits', 0),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = get_supabase().table('plumbers').insert(data).execute()
            if result.data:
                return cls(**result.data[0])
            return None
        except Exception as e:
            print(f"Error creating plumber: {str(e)}")
            return None
    
    @classmethod
    def get_by_id(cls, plumber_id):
        """Get a plumber by ID from Supabase."""
        try:
            result = get_supabase().table('plumbers').select('*').eq('id', plumber_id).execute()
            if result.data:
                return cls(**result.data[0])
            return None
        except Exception as e:
            print(f"Error getting plumber by ID: {str(e)}")
            return None
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Get a plumber by user ID from Supabase."""
        try:
            result = get_supabase().table('plumbers').select('*').eq('user_id', user_id).execute()
            if result.data:
                return cls(**result.data[0])
            return None
        except Exception as e:
            print(f"Error getting plumber by user ID: {str(e)}")
            return None
    
    def save(self):
        """Update the plumber profile in Supabase."""
        try:
            data = {
                'company_name': self.company_name,
                'contact_name': self.contact_name,
                'phone': self.phone,
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'service_radius': self.service_radius,
                'services_offered': self.services_offered,
                'license_number': self.license_number,
                'is_insured': self.is_insured,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'is_active': self.is_active,
                'subscription_status': self.subscription_status,
                'stripe_customer_id': self.stripe_customer_id,
                'stripe_subscription_id': self.stripe_subscription_id,
                'lead_credits': self.lead_credits,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = get_supabase().table('plumbers').update(data).eq('id', self.id).execute()
            if result.data:
                return True
            return False
        except Exception as e:
            print(f"Error updating plumber: {str(e)}")
            return False
    
    def add_lead_credits(self, count):
        """Add lead credits to the plumber's account."""
        try:
            self.lead_credits += count
            return self.save()
        except Exception as e:
            print(f"Error adding lead credits: {str(e)}")
            return False
    
    @classmethod
    def find_by_location(cls, latitude, longitude, radius_miles, services=None):
        """Find plumbers within a radius of a location."""
        # In a real implementation, this would query the database
        # For now, return an empty list
        return [] 

    @classmethod
    def count_all(cls):
        """Count all plumbers in the database."""
        logger.info("Counting all plumbers")
        
        try:
            # For development/testing, return a mock count
            # In a real implementation, this would query the database
            return 12
        except Exception as e:
            logger.error(f"Error counting plumbers: {str(e)}", exc_info=True)
            return 0

    @classmethod
    def get_recent(cls, limit=5):
        """Retrieve recent plumbers."""
        logger.info(f"Fetching {limit} recent plumbers")
        
        try:
            # For development/testing, return mock plumbers
            # In a real implementation, this would query the database
            plumbers = []
            for i in range(1, limit + 1):
                plumbers.append(cls(
                    id=f"plumber-{i}",
                    user_id=f"user-{i}",
                    company_name=f"Plumber Company {i}",
                    contact_name=f"Contact {i}",
                    email=f"plumber{i}@example.com",
                    phone=f"555-987-{i:04d}",
                    lead_credits=i * 5,
                    is_active=i % 4 != 0,  # 75% active
                    subscription_status="active" if i % 3 != 0 else "inactive"
                ))
            return plumbers
        except Exception as e:
            logger.error(f"Error fetching recent plumbers: {str(e)}", exc_info=True)
            return []

    @classmethod
    def get_all(cls):
        """Retrieve all plumbers."""
        logger.info("Fetching all plumbers")
        
        try:
            # For development/testing, return mock plumbers
            # In a real implementation, this would query the database
            plumbers = []
            for i in range(1, 11):
                plumbers.append(cls(
                    id=f"plumber-{i}",
                    user_id=f"user-{i}",
                    company_name=f"Plumber Company {i}",
                    contact_name=f"Contact {i}",
                    email=f"plumber{i}@example.com",
                    phone=f"555-987-{i:04d}",
                    lead_credits=i * 5,
                    is_active=i % 4 != 0,  # 75% active
                    subscription_status="active" if i % 3 != 0 else "inactive"
                ))
            return plumbers
        except Exception as e:
            logger.error(f"Error fetching all plumbers: {str(e)}", exc_info=True)
            return []

    @classmethod
    def filter(cls, status=None):
        """Filter plumbers by criteria."""
        logger.info(f"Filtering plumbers with status={status}")
        
        try:
            # For development/testing, return filtered mock plumbers
            # In a real implementation, this would query the database
            all_plumbers = cls.get_all()
            filtered_plumbers = []
            
            for plumber in all_plumbers:
                # Apply status filter if provided
                if status == 'active' and not plumber.is_active:
                    continue
                if status == 'inactive' and plumber.is_active:
                    continue
                
                filtered_plumbers.append(plumber)
            
            return filtered_plumbers
        except Exception as e:
            logger.error(f"Error filtering plumbers: {str(e)}", exc_info=True)
            return [] 
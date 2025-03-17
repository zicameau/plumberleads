from datetime import datetime
import uuid
import logging
import json
from app.services.auth_service import get_supabase

# Get the database logger
logger = logging.getLogger('database')

class Plumber:
    """
    Plumber model for service providers.
    Maps to the 'plumbers' table in Supabase.
    """
    TABLE_NAME = 'plumbers'
    
    def __init__(self, id=None, user_id=None, company_name=None, contact_name=None,
                 email=None, phone=None, address=None, city=None, state=None,
                 zip_code=None, service_radius=25, services_offered=None,
                 license_number=None, is_insured=False, latitude=None, longitude=None,
                 is_active=True, subscription_status='inactive', stripe_customer_id=None,
                 stripe_subscription_id=None, lead_credits=0, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.company_name = company_name
        self.contact_name = contact_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.service_radius = service_radius
        self.services_offered = services_offered or []
        self.license_number = license_number
        self.is_insured = is_insured
        self.latitude = latitude
        self.longitude = longitude
        self.is_active = is_active
        self.subscription_status = subscription_status
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.lead_credits = lead_credits
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @classmethod
    def create(cls, plumber_data):
        """Create a new plumber profile in the database."""
        logger.info(f"Creating new plumber: {plumber_data.get('company_name')} for user {plumber_data.get('user_id')}")
        
        try:
            supabase = get_supabase()
            response = supabase.table(cls.TABLE_NAME).insert(plumber_data).execute()
            if response.data:
                plumber = cls(**response.data[0])
                logger.info(f"Successfully created plumber with ID {plumber.id}")
                return plumber
            return None
        except Exception as e:
            logger.error(f"Failed to create plumber: {str(e)}", exc_info=True)
            return None
    
    @classmethod
    def get_by_id(cls, plumber_id):
        """Retrieve a plumber by ID."""
        logger.info(f"Fetching plumber with ID {plumber_id}")
        
        try:
            supabase = get_supabase()
            response = supabase.table(cls.TABLE_NAME).select('*').eq('id', plumber_id).execute()
            if response.data:
                return cls(**response.data[0])
            logger.info(f"Plumber with ID {plumber_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching plumber with ID {plumber_id}: {str(e)}", exc_info=True)
            return None
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Retrieve a plumber profile by user ID."""
        logger.info(f"Fetching plumber by user ID {user_id}")
        
        try:
            supabase = get_supabase()
            response = supabase.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).execute()
            if response.data:
                return cls(**response.data[0])
            logger.info(f"Plumber with user ID {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching plumber with user ID {user_id}: {str(e)}", exc_info=True)
            return None

    @classmethod
    def get_by_email(cls, email):
        """Retrieve a plumber by email."""
        logger.info(f"Fetching plumber with email {email}")
        
        try:
            supabase = get_supabase()
            response = supabase.table(cls.TABLE_NAME).select('*').eq('email', email).execute()
            if response.data:
                return cls(**response.data[0])
            logger.info(f"Plumber with email {email} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching plumber with email {email}: {str(e)}", exc_info=True)
            return None
    
    def save(self):
        """Update plumber profile."""
        logger.info(f"Updating plumber profile for ID {self.id}")
        
        try:
            supabase = get_supabase()
            self.updated_at = datetime.utcnow()
            response = supabase.table(self.TABLE_NAME).update(self.__dict__).eq('id', self.id).execute()
            if response.data:
                logger.info(f"Successfully updated plumber profile for ID {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update plumber profile for ID {self.id}: {str(e)}", exc_info=True)
            return False
    
    def add_lead_credits(self, count):
        """Add lead credits to plumber account."""
        logger.info(f"Adding {count} lead credits to plumber {self.id}")
        
        try:
            previous_credits = self.lead_credits
            self.lead_credits += count
            if self.save():
                logger.info(f"Updated lead credits for plumber {self.id} from {previous_credits} to {self.lead_credits}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add lead credits to plumber {self.id}: {str(e)}", exc_info=True)
            return False
    
    @classmethod
    def find_by_location(cls, latitude, longitude, radius_miles, services=None):
        """Find plumbers within a radius of a location."""
        try:
            supabase = get_supabase()
            # In a real implementation, this would use PostGIS to find plumbers within radius
            # For now, return all plumbers
            response = supabase.table(cls.TABLE_NAME).select('*').execute()
            return [cls(**plumber) for plumber in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Error finding plumbers by location: {str(e)}", exc_info=True)
            return []

    @classmethod
    def count_all(cls):
        """Count all plumbers in the database."""
        logger.info("Counting all plumbers")
        
        try:
            supabase = get_supabase()
            response = supabase.table(cls.TABLE_NAME).select('id', count='exact').execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            logger.error(f"Error counting plumbers: {str(e)}", exc_info=True)
            return 0

    @classmethod
    def get_recent(cls, limit=5):
        """Retrieve recent plumbers."""
        logger.info(f"Fetching {limit} recent plumbers")
        
        try:
            supabase = get_supabase()
            response = supabase.table(cls.TABLE_NAME).select('*').order('created_at', desc=True).limit(limit).execute()
            return [cls(**plumber) for plumber in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Error fetching recent plumbers: {str(e)}", exc_info=True)
            return []

    @classmethod
    def get_all(cls):
        """Retrieve all plumbers."""
        logger.info("Fetching all plumbers")
        
        try:
            supabase = get_supabase()
            response = supabase.table(cls.TABLE_NAME).select('*').execute()
            return [cls(**plumber) for plumber in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Error fetching all plumbers: {str(e)}", exc_info=True)
            return []

    @classmethod
    def filter(cls, status=None):
        """Filter plumbers by criteria."""
        logger.info(f"Filtering plumbers with status={status}")
        
        try:
            supabase = get_supabase()
            query = supabase.table(cls.TABLE_NAME).select('*')
            
            if status == 'active':
                query = query.eq('is_active', True)
            elif status == 'inactive':
                query = query.eq('is_active', False)
            
            response = query.execute()
            return [cls(**plumber) for plumber in response.data] if response.data else []
        except Exception as e:
            logger.error(f"Error filtering plumbers: {str(e)}", exc_info=True)
            return [] 
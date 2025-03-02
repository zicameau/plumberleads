# app/models/lead.py
from datetime import datetime
from app.services.auth_service import get_supabase_client


class Lead:
    """
    Lead model for customer service requests.
    Maps to the 'leads' table in Supabase.
    """
    TABLE_NAME = 'leads'
    
    def __init__(self, id=None, customer_name=None, email=None, phone=None, 
                 address=None, city=None, state=None, zip_code=None,
                 problem_description=None, service_needed=None, urgency=None,
                 latitude=None, longitude=None, created_at=None, status=None):
        self.id = id
        self.customer_name = customer_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.problem_description = problem_description
        self.service_needed = service_needed
        self.urgency = urgency
        self.latitude = latitude
        self.longitude = longitude
        self.created_at = created_at or datetime.utcnow()
        self.status = status or 'new'  # new, matched, claimed, completed
    
    @classmethod
    def create(cls, lead_data):
        """Create a new lead in the database."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).insert(lead_data).execute()
        return cls(**response.data[0]) if response.data else None
    
    @classmethod
    def get_by_id(cls, lead_id):
        """Retrieve a lead by ID."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).select('*').eq('id', lead_id).execute()
        return cls(**response.data[0]) if response.data else None
    
    @classmethod
    def find_by_location(cls, latitude, longitude, radius_miles=25, limit=20):
        """
        Find leads within the specified radius of the given coordinates.
        
        This requires using a PostGIS extension in Supabase or a custom function.
        For simplicity, we'll use a direct SQL query with the ST_DWithin function.
        """
        supabase = get_supabase_client()
        # Convert miles to meters (1 mile ≈ 1609.34 meters)
        radius_meters = radius_miles * 1609.34
        
        # Using PostGIS functions requires custom SQL
        query = f"""
        SELECT * FROM {cls.TABLE_NAME}
        WHERE ST_DWithin(
            ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography,
            ST_SetSRID(ST_MakePoint({longitude}, {latitude}), 4326)::geography,
            {radius_meters}
        )
        AND status = 'new'
        ORDER BY created_at DESC
        LIMIT {limit}
        """
        
        response = supabase.rpc('find_leads_by_location', {
            'lat': latitude,
            'lng': longitude,
            'radius_miles': radius_miles,
            'status': 'new',
            'limit_count': limit
        }).execute()
        
        return [cls(**lead) for lead in response.data] if response.data else []
    
    @classmethod
    def update_status(cls, lead_id, new_status):
        """Update the status of a lead."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).update({
            'status': new_status,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', lead_id).execute()
        
        return cls(**response.data[0]) if response.data else None


# app/models/plumber.py

class Plumber:
    """
    Plumber model for service providers.
    Maps to the 'plumbers' table in Supabase.
    """
    TABLE_NAME = 'plumbers'
    
    def __init__(self, id=None, user_id=None, company_name=None, contact_name=None,
                 email=None, phone=None, address=None, city=None, state=None,
                 zip_code=None, service_radius=None, services_offered=None,
                 license_number=None, is_insured=None, latitude=None, longitude=None,
                 is_active=None, subscription_status=None, stripe_customer_id=None,
                 stripe_subscription_id=None, lead_credits=None, created_at=None):
        self.id = id
        self.user_id = user_id  # References auth.users in Supabase
        self.company_name = company_name
        self.contact_name = contact_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.service_radius = service_radius or 25  # Default radius in miles
        self.services_offered = services_offered or []
        self.license_number = license_number
        self.is_insured = is_insured
        self.latitude = latitude
        self.longitude = longitude
        self.is_active = is_active if is_active is not None else True
        self.subscription_status = subscription_status or 'inactive'
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.lead_credits = lead_credits or 0
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def create(cls, plumber_data):
        """Create a new plumber profile in the database."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).insert(plumber_data).execute()
        return cls(**response.data[0]) if response.data else None
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Retrieve a plumber profile by user ID."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).execute()
        return cls(**response.data[0]) if response.data else None
    
    @classmethod
    def find_by_location(cls, latitude, longitude, radius_miles=50, services=None, limit=50):
        """
        Find plumbers within the specified radius of the given coordinates,
        optionally filtered by services offered.
        """
        supabase = get_supabase_client()
        
        # Using a stored procedure for complex geo queries
        params = {
            'lat': latitude,
            'lng': longitude,
            'radius_miles': radius_miles,
            'limit_count': limit,
            'services': services or []
        }
        
        response = supabase.rpc('find_plumbers_by_location', params).execute()
        
        return [cls(**plumber) for plumber in response.data] if response.data else []
    
    def update_subscription(self, subscription_status, stripe_subscription_id=None):
        """Update the subscription status for a plumber."""
        supabase = get_supabase_client()
        update_data = {
            'subscription_status': subscription_status,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if stripe_subscription_id:
            update_data['stripe_subscription_id'] = stripe_subscription_id
        
        response = supabase.table(self.TABLE_NAME).update(update_data).eq('id', self.id).execute()
        
        if response.data:
            self.subscription_status = subscription_status
            if stripe_subscription_id:
                self.stripe_subscription_id = stripe_subscription_id
            return True
        return False
    
    def add_lead_credits(self, amount):
        """Add lead credits to the plumber's account."""
        supabase = get_supabase_client()
        response = supabase.table(self.TABLE_NAME).update({
            'lead_credits': self.lead_credits + amount,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', self.id).execute()
        
        if response.data:
            self.lead_credits += amount
            return True
        return False
    
    def use_lead_credit(self):
        """Use a lead credit when a plumber claims a lead."""
        if self.lead_credits <= 0:
            return False
            
        supabase = get_supabase_client()
        response = supabase.table(self.TABLE_NAME).update({
            'lead_credits': self.lead_credits - 1,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', self.id).execute()
        
        if response.data:
            self.lead_credits -= 1
            return True
        return False


# app/models/lead_claim.py

class LeadClaim:
    """
    Model for tracking which plumbers have claimed which leads.
    Maps to the 'lead_claims' table in Supabase.
    """
    TABLE_NAME = 'lead_claims'
    
    def __init__(self, id=None, lead_id=None, plumber_id=None, 
                 claimed_at=None, status=None, contact_status=None,
                 notes=None):
        self.id = id
        self.lead_id = lead_id
        self.plumber_id = plumber_id
        self.claimed_at = claimed_at or datetime.utcnow()
        self.status = status or 'new'  # new, contacted, completed, abandoned
        self.contact_status = contact_status  # attempted, reached, no-answer, etc.
        self.notes = notes
    
    @classmethod
    def create(cls, claim_data):
        """Create a new lead claim in the database."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).insert(claim_data).execute()
        return cls(**response.data[0]) if response.data else None
    
    @classmethod
    def get_by_lead_and_plumber(cls, lead_id, plumber_id):
        """Get a claim by lead and plumber ID combination."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).select('*')\
            .eq('lead_id', lead_id)\
            .eq('plumber_id', plumber_id)\
            .execute()
        
        return cls(**response.data[0]) if response.data else None
    
    @classmethod
    def get_by_lead(cls, lead_id):
        """Get all claims for a specific lead."""
        supabase = get_supabase_client()
        response = supabase.table(cls.TABLE_NAME).select('*')\
            .eq('lead_id', lead_id)\
            .execute()
        
        return [cls(**claim) for claim in response.data] if response.data else []
    
    @classmethod
    def get_by_plumber(cls, plumber_id, status=None, limit=50, offset=0):
        """Get all claims for a specific plumber, optionally filtered by status."""
        supabase = get_supabase_client()
        query = supabase.table(cls.TABLE_NAME).select('*')\
            .eq('plumber_id', plumber_id)
            
        if status:
            query = query.eq('status', status)
            
        response = query.order('claimed_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return [cls(**claim) for claim in response.data] if response.data else []
    
    def update_status(self, new_status, contact_status=None, notes=None):
        """Update the status of a lead claim."""
        supabase = get_supabase_client()
        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if contact_status:
            update_data['contact_status'] = contact_status
            
        if notes:
            update_data['notes'] = notes
            
        response = supabase.table(self.TABLE_NAME).update(update_data)\
            .eq('id', self.id)\
            .execute()
        
        if response.data:
            self.status = new_status
            if contact_status:
                self.contact_status = contact_status
            if notes:
                self.notes = notes
            return True
        return False

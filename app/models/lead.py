from datetime import datetime
import uuid

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
        self.id = id or str(uuid.uuid4())
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
        # In a real implementation, this would save to the database
        # For now, just create an instance
        return cls(**lead_data)
    
    @classmethod
    def get_by_id(cls, lead_id):
        """Retrieve a lead by ID."""
        # In a real implementation, this would query the database
        # For now, return None
        return None
    
    @classmethod
    def get_by_reference(cls, reference):
        """Retrieve a lead by reference code."""
        # In a real implementation, this would query the database
        # For now, return None
        return None
    
    @classmethod
    def find_by_location(cls, latitude, longitude, radius_miles, limit=10):
        """Find leads within a radius of a location."""
        # In a real implementation, this would query the database
        # For now, return an empty list
        return [] 
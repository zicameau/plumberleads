from datetime import datetime
import uuid
import logging

# Get the database logger
logger = logging.getLogger('database')

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
        logger.info(f"Fetching lead by ID {lead_id}")
        
        try:
            # For development/testing, return a mock lead
            # In a real implementation, this would query the database
            if lead_id:
                return cls(
                    id=lead_id,
                    customer_name="Test Customer",
                    email="customer@example.com",
                    phone="555-123-4567",
                    address="123 Main St",
                    city="Anytown",
                    state="CA",
                    zip_code="12345",
                    problem_description="Water leak under the sink",
                    service_needed="leak",
                    urgency="medium",
                    latitude=34.0522,
                    longitude=-118.2437,
                    created_at=datetime.utcnow()
                )
            return None
        except Exception as e:
            logger.error(f"Error fetching lead {lead_id}: {str(e)}", exc_info=True)
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

    @classmethod
    def count_all(cls):
        """Count all leads in the database."""
        logger.info("Counting all leads")
        
        try:
            # For development/testing, return a mock count
            # In a real implementation, this would query the database
            return 25
        except Exception as e:
            logger.error(f"Error counting leads: {str(e)}", exc_info=True)
            return 0
    
    @classmethod
    def get_all(cls):
        """Retrieve all leads."""
        logger.info("Fetching all leads")
        
        try:
            # For development/testing, return mock leads
            # In a real implementation, this would query the database
            leads = []
            for i in range(1, 11):
                leads.append(cls(
                    id=f"lead-{i}",
                    customer_name=f"Customer {i}",
                    email=f"customer{i}@example.com",
                    phone=f"555-123-{i:04d}",
                    address=f"{i} Main St",
                    city="Anytown",
                    state="CA",
                    zip_code="12345",
                    problem_description=f"Service request {i}",
                    service_needed="leak" if i % 3 == 0 else "toilet" if i % 3 == 1 else "drain",
                    urgency="high" if i % 3 == 0 else "medium" if i % 3 == 1 else "low",
                    status="new" if i % 4 == 0 else "assigned" if i % 4 == 1 else "in_progress" if i % 4 == 2 else "completed",
                    created_at=datetime.utcnow()
                ))
            return leads
        except Exception as e:
            logger.error(f"Error fetching all leads: {str(e)}", exc_info=True)
            return []
    
    @classmethod
    def get_recent(cls, limit=5):
        """Retrieve recent leads."""
        logger.info(f"Fetching {limit} recent leads")
        
        try:
            # For development/testing, return mock leads
            # In a real implementation, this would query the database
            leads = []
            for i in range(1, limit + 1):
                leads.append(cls(
                    id=f"lead-{i}",
                    customer_name=f"Customer {i}",
                    email=f"customer{i}@example.com",
                    phone=f"555-123-{i:04d}",
                    address=f"{i} Main St",
                    city="Anytown",
                    state="CA",
                    zip_code="12345",
                    problem_description=f"Service request {i}",
                    service_needed="leak" if i % 3 == 0 else "toilet" if i % 3 == 1 else "drain",
                    urgency="high" if i % 3 == 0 else "medium" if i % 3 == 1 else "low",
                    status="new" if i % 4 == 0 else "assigned" if i % 4 == 1 else "in_progress" if i % 4 == 2 else "completed",
                    created_at=datetime.utcnow()
                ))
            return leads
        except Exception as e:
            logger.error(f"Error fetching recent leads: {str(e)}", exc_info=True)
            return []
    
    @classmethod
    def filter(cls, status=None, start_date=None, end_date=None):
        """Filter leads by criteria."""
        logger.info(f"Filtering leads with status={status}, start_date={start_date}, end_date={end_date}")
        
        try:
            # For development/testing, return filtered mock leads
            # In a real implementation, this would query the database
            all_leads = cls.get_all()
            filtered_leads = []
            
            for lead in all_leads:
                # Apply status filter if provided
                if status and lead.status != status:
                    continue
                
                # Apply date filters if provided
                if start_date and lead.created_at < start_date:
                    continue
                if end_date and lead.created_at > end_date:
                    continue
                
                filtered_leads.append(lead)
            
            return filtered_leads
        except Exception as e:
            logger.error(f"Error filtering leads: {str(e)}", exc_info=True)
            return [] 
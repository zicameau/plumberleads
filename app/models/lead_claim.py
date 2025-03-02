from datetime import datetime
import uuid

class LeadClaim:
    """
    Lead claim model for tracking plumber claims on leads.
    Maps to the 'lead_claims' table in Supabase.
    """
    TABLE_NAME = 'lead_claims'
    
    def __init__(self, id=None, lead_id=None, plumber_id=None, status='new',
                 notes=None, claimed_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.lead_id = lead_id
        self.plumber_id = plumber_id
        self.status = status  # new, contacted, completed, abandoned
        self.notes = notes
        self.claimed_at = claimed_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @classmethod
    def get_by_lead(cls, lead_id):
        """Get all claims for a specific lead."""
        # In a real implementation, this would query the database
        # For now, return an empty list
        return []
    
    @classmethod
    def get_by_plumber(cls, plumber_id):
        """Get all claims for a specific plumber."""
        # In a real implementation, this would query the database
        # For now, return an empty list
        return [] 
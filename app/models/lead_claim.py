from datetime import datetime
import logging

# Get the database logger
logger = logging.getLogger('database')

class LeadClaim:
    """
    LeadClaim model for tracking which plumbers have claimed which leads.
    Maps to the 'lead_claims' table in the database.
    """
    TABLE_NAME = 'lead_claims'
    
    def __init__(self, id=None, lead_id=None, plumber_id=None, claimed_at=None,
                 status='claimed', contacted_at=None, notes=None):
        self.id = id
        self.lead_id = lead_id
        self.plumber_id = plumber_id
        self.claimed_at = claimed_at or datetime.utcnow()
        self.status = status
        self.contacted_at = contacted_at
        self.notes = notes
    
    @classmethod
    def count_all(cls):
        """Count all lead claims in the database."""
        logger.info("Counting all lead claims")
        
        try:
            # For development/testing, return a mock count
            # In a real implementation, this would query the database
            return 15
        except Exception as e:
            logger.error(f"Error counting lead claims: {str(e)}", exc_info=True)
            return 0
    
    @classmethod
    def count_unique_leads(cls):
        """Count unique leads that have been claimed."""
        logger.info("Counting unique claimed leads")
        
        try:
            # For development/testing, return a mock count
            # In a real implementation, this would query the database
            return 10
        except Exception as e:
            logger.error(f"Error counting unique claimed leads: {str(e)}", exc_info=True)
            return 0
    
    @classmethod
    def get_by_plumber(cls, plumber_id, limit=None):
        """Retrieve claims by plumber ID."""
        logger.info(f"Fetching claims for plumber {plumber_id}")
        
        try:
            # For development/testing, return mock claims
            # In a real implementation, this would query the database
            claims = []
            count = limit or 5
            for i in range(1, count + 1):
                claims.append(cls(
                    id=f"claim-{i}",
                    lead_id=f"lead-{i}",
                    plumber_id=plumber_id,
                    claimed_at=datetime.utcnow(),
                    status="contacted" if i % 3 == 0 else "claimed",
                    contacted_at=datetime.utcnow() if i % 3 == 0 else None
                ))
            return claims
        except Exception as e:
            logger.error(f"Error fetching claims for plumber {plumber_id}: {str(e)}", exc_info=True)
            return []
    
    @classmethod
    def get_by_lead_and_plumber(cls, lead_id, plumber_id):
        """Check if a lead has been claimed by a specific plumber."""
        logger.info(f"Checking if lead {lead_id} is claimed by plumber {plumber_id}")
        
        try:
            # For development/testing, return None (not claimed)
            # In a real implementation, this would query the database
            return None
        except Exception as e:
            logger.error(f"Error checking claim for lead {lead_id} and plumber {plumber_id}: {str(e)}", exc_info=True)
            return None
    
    @classmethod
    def get_recent(cls, limit=5):
        """Retrieve recent claims."""
        logger.info(f"Fetching {limit} recent claims")
        
        try:
            # For development/testing, return mock claims
            # In a real implementation, this would query the database
            claims = []
            for i in range(1, limit + 1):
                claims.append(cls(
                    id=f"claim-{i}",
                    lead_id=f"lead-{i}",
                    plumber_id=f"plumber-{i}",
                    claimed_at=datetime.utcnow(),
                    status="contacted" if i % 3 == 0 else "claimed",
                    contacted_at=datetime.utcnow() if i % 3 == 0 else None
                ))
            return claims
        except Exception as e:
            logger.error(f"Error fetching recent claims: {str(e)}", exc_info=True)
            return []
    
    @classmethod
    def create(cls, claim_data):
        """Create a new lead claim."""
        logger.info(f"Creating claim for lead {claim_data.get('lead_id')} by plumber {claim_data.get('plumber_id')}")
        
        try:
            # For development/testing, return a mock claim
            # In a real implementation, this would insert into the database
            return cls(
                id=f"claim-new",
                lead_id=claim_data.get('lead_id'),
                plumber_id=claim_data.get('plumber_id'),
                claimed_at=claim_data.get('claimed_at') or datetime.utcnow(),
                status="claimed"
            )
        except Exception as e:
            logger.error(f"Error creating claim: {str(e)}", exc_info=True)
            return None 
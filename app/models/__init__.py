# Import models here to make them available when importing from models package 
from app.models.user import User
from app.models.lead import Lead
from app.models.payment import Payment
from app.models.lead_history import LeadHistory

__all__ = ['User', 'Lead', 'Payment', 'LeadHistory'] 
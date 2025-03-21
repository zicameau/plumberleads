from app import db
from app.models.lead_history import LeadHistory
from datetime import datetime

def log_lead_change(lead, field_name, old_value, new_value, change_type, user_id=None):
    """
    Log a change to a lead.
    
    Args:
        lead: The Lead model instance
        field_name: Name of the field that changed
        old_value: Previous value
        new_value: New value
        change_type: Type of change (e.g., 'status_change', 'price_update')
        user_id: ID of the user who made the change (optional)
    """
    history_entry = LeadHistory(
        lead_id=lead.id,
        user_id=user_id,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        change_type=change_type
    )
    db.session.add(history_entry)
    db.session.commit()

def get_lead_history(lead_id, limit=None):
    """
    Get the history of changes for a lead.
    
    Args:
        lead_id: ID of the lead
        limit: Maximum number of history entries to return (optional)
    
    Returns:
        List of LeadHistory entries
    """
    query = LeadHistory.query.filter_by(lead_id=lead_id).order_by(LeadHistory.created_at.desc())
    if limit:
        query = query.limit(limit)
    return query.all() 
from app import db
from datetime import datetime
import uuid

class LeadHistory(db.Model):
    """Model for tracking changes to leads."""
    __tablename__ = 'lead_history'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('leads.id'), nullable=False)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'))
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(255))
    new_value = db.Column(db.String(255))
    change_type = db.Column(db.String(50), nullable=False)  # e.g., 'status_change', 'price_update', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = db.relationship('Lead', backref=db.backref(
        'history',
        lazy='dynamic',
        order_by='LeadHistory.created_at.desc()'
    ))
    user = db.relationship('User')

    @classmethod
    def log_status_change(cls, lead, old_status, new_status, user_id=None):
        """Helper method to log a status change."""
        return cls(
            lead_id=lead.id,
            user_id=user_id or lead.reserved_by_id,
            field_name='status',
            old_value=old_status,
            new_value=new_status,
            change_type='status_change'
        )

    @classmethod
    def log_price_change(cls, lead, old_price, new_price, user_id=None):
        """Helper method to log a price change."""
        return cls(
            lead_id=lead.id,
            user_id=user_id or lead.reserved_by_id,
            field_name='price',
            old_value=str(old_price),
            new_value=str(new_price),
            change_type='price_update'
        )

    @classmethod
    def log_reservation(cls, lead, user_id):
        """Helper method to log a lead reservation."""
        return cls(
            lead_id=lead.id,
            user_id=user_id,
            field_name='reserved_by_id',
            old_value=None,
            new_value=str(user_id),
            change_type='reservation'
        )

    def to_dict(self):
        """Convert the history entry to a dictionary."""
        return {
            'id': str(self.id),
            'lead_id': str(self.lead_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'change_type': self.change_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<LeadHistory {self.id}: {self.lead_id} - {self.field_name}>' 
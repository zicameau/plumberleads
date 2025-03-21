from datetime import datetime, timedelta
from app import db
import uuid
from sqlalchemy import event
from app.models.lead_history import LeadHistory

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    service_type = db.Column(db.String(100), nullable=False)
    service_details = db.Column(db.Text)
    urgency = db.Column(db.String(20), nullable=False, default='medium')
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(200))
    customer_phone = db.Column(db.String(20))
    source = db.Column(db.String(50), default='website')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reserved_at = db.Column(db.DateTime)
    reserved_by_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'))
    
    # Relationships
    payment = db.relationship('Payment', backref='lead', uselist=False)
    reserved_by = db.relationship('User', foreign_keys=[reserved_by_id], back_populates='reserved_leads')
    
    def to_dict(self, include_contact=False):
        """Convert to dictionary, optionally including contact info"""
        data = {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'service_type': self.service_type,
            'service_details': self.service_details,
            'urgency': self.urgency,
            'price': self.price,
            'status': self.status,
            'reserved_at': self.reserved_at.isoformat() if self.reserved_at else None,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Only include contact info if requested and lead is claimed
        if include_contact and self.status == 'claimed':
            data.update({
                'customer_name': self.customer_name,
                'customer_email': self.customer_email,
                'customer_phone': self.customer_phone,
                'address': self.address,
                'notes': self.notes
            })
            
        return data
    
    def reserve(self, user_id):
        """Reserve a lead for a user."""
        old_status = self.status
        self.status = 'reserved'
        self.reserved_by_id = user_id
        self.reserved_at = datetime.utcnow()
        
        # Log the changes
        db.session.add(LeadHistory.log_status_change(self, old_status, 'reserved', user_id))
        db.session.add(LeadHistory.log_reservation(self, user_id))
        
        db.session.commit()
        
    def release(self):
        """Release a reserved lead."""
        old_status = self.status
        self.status = 'available'
        self.reserved_by_id = None
        self.reserved_at = None
        
        # Log the status change
        db.session.add(LeadHistory.log_status_change(self, old_status, 'available'))
        
        db.session.commit()
        
    def claim(self, user_id):
        """Claim a lead after payment."""
        old_status = self.status
        self.status = 'claimed'
        
        # Log the status change
        db.session.add(LeadHistory.log_status_change(self, old_status, 'claimed', user_id))
        
        db.session.commit()
        
    def update_status(self, status):
        """Update the status of this lead"""
        valid_statuses = ['available', 'reserved', 'claimed', 'completed', 'closed']
        if status in valid_statuses:
            old_status = self.status
            self.status = status
            
            # Log the status change
            db.session.add(LeadHistory.log_status_change(self, old_status, status))
            
            return True
        return False
    
    def is_reservation_expired(self, max_minutes=60):
        """Check if the lead reservation has expired"""
        if not self.reserved_at:
            return False
        expiration_time = self.reserved_at + timedelta(minutes=max_minutes)
        return datetime.utcnow() > expiration_time
    
    def __repr__(self):
        return f'<Lead {self.id}: {self.title}>'

# Track changes to Lead model
@event.listens_for(Lead, 'after_update')
def track_lead_changes(mapper, connection, target):
    """Track changes to lead fields."""
    for attr in mapper.attrs:
        if attr.key in ['status', 'price', 'reserved_by_id']:
            old_value = getattr(target, attr.key)
            new_value = getattr(target, attr.key)
            
            if old_value != new_value:
                if attr.key == 'status':
                    db.session.add(LeadHistory.log_status_change(target, old_value, new_value))
                elif attr.key == 'price':
                    db.session.add(LeadHistory.log_price_change(target, old_value, new_value))
                elif attr.key == 'reserved_by_id':
                    db.session.add(LeadHistory.log_reservation(target, new_value)) 
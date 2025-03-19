from datetime import datetime
from app import db
import uuid

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    service_details = db.Column(db.Text)
    urgency = db.Column(db.String(20), default='normal') # low, normal, high, emergency
    price = db.Column(db.Float, nullable=False)
    is_claimed = db.Column(db.Boolean, default=False)
    claimed_at = db.Column(db.DateTime)
    plumber_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='new') # new, contacted, scheduled, completed, closed
    notes = db.Column(db.Text)
    source = db.Column(db.String(50), default='website') # website, facebook, google, manual
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payment = db.relationship('Payment', backref='lead', uselist=False)
    
    def to_dict(self, include_contact=False):
        """Convert to dictionary, optionally including contact info"""
        data = {
            'id': str(self.id),  # Convert UUID to string
            'title': self.title,
            'description': self.description,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'service_type': self.service_type,
            'service_details': self.service_details,
            'urgency': self.urgency,
            'price': self.price,
            'is_claimed': self.is_claimed,
            'claimed_at': self.claimed_at.isoformat() if self.claimed_at else None,
            'status': self.status,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Only include contact info if requested (e.g., for claimed leads)
        if include_contact:
            data.update({
                'customer_name': self.customer_name,
                'customer_email': self.customer_email,
                'customer_phone': self.customer_phone,
                'address': self.address,
                'notes': self.notes
            })
            
        return data
    
    def claim(self, plumber_id):
        """Claim this lead for a plumber"""
        self.is_claimed = True
        self.plumber_id = plumber_id
        self.claimed_at = datetime.utcnow()
        self.status = 'claimed'
        
    def update_status(self, status):
        """Update the status of this lead"""
        valid_statuses = ['new', 'claimed', 'contacted', 'scheduled', 'completed', 'closed']
        if status in valid_statuses:
            self.status = status
            return True
        return False
    
    def __repr__(self):
        return f'<Lead {self.id}: {self.title}>' 
from datetime import datetime
from app import db
from flask import current_app
import json
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(255))
    business_description = db.Column(db.Text, nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    has_insurance = db.Column(db.Boolean, default=False)
    # Address fields
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    service_radius = db.Column(db.Integer, nullable=False, default=25)  # Default 25 mile radius
    service_areas = db.Column(db.Text, nullable=False) # JSON string of service areas
    service_types = db.Column(db.Text, nullable=False) # JSON string of service types
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reserved_leads = db.relationship('Lead', foreign_keys='Lead.reserved_by_id', back_populates='reserved_by', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    def set_service_areas(self, areas):
        """Set service areas as a JSON string"""
        self.service_areas = json.dumps(areas)
        
    def get_service_areas(self):
        """Get service areas as a list"""
        if not self.service_areas:
            return []
        return json.loads(self.service_areas)
    
    def set_service_types(self, types):
        """Set service types as a JSON string"""
        self.service_types = json.dumps(types)
        
    def get_service_types(self):
        """Get service types as a list"""
        if not self.service_types:
            return []
        return json.loads(self.service_types)
    
    def is_verified(self, verification_status=None):
        """Check if the user's email is verified.
        If verification_status is provided, use that instead of checking Supabase."""
        if verification_status is not None:
            return verification_status
        return False  # Default to False if no status provided
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_verified': self.is_verified(),  # This will now return False by default
            'profile_image': self.profile_image,
            'business_description': self.business_description,
            'license_number': self.license_number,
            'has_insurance': self.has_insurance,
            'service_areas': self.get_service_areas(),
            'service_types': self.get_service_types(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.full_name}>' 
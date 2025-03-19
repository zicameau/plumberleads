from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    profile_image = db.Column(db.String(255))
    business_description = db.Column(db.Text)
    license_number = db.Column(db.String(50))
    has_insurance = db.Column(db.Boolean, default=False)
    service_areas = db.Column(db.Text) # JSON string of service areas
    service_types = db.Column(db.Text) # JSON string of service types
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leads = db.relationship('Lead', backref='plumber', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
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
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 
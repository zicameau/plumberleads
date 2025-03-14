"""SQLAlchemy models that sync with Supabase schema."""
from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Enum, Text, JSON, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
import uuid

# Initialize SQLAlchemy
db = SQLAlchemy()
Base = declarative_base()

# Enum types to match database schema
class UserRole(enum.Enum):
    admin = "admin"
    plumber = "plumber"

class LeadStatus(enum.Enum):
    new = "new"
    matched = "matched"
    claimed = "claimed"
    completed = "completed"

class ClaimStatus(enum.Enum):
    new = "new"
    contacted = "contacted"
    completed = "completed"
    abandoned = "abandoned"

class ContactStatus(enum.Enum):
    attempted = "attempted"
    reached = "reached"
    no_answer = "no-answer"
    scheduled = "scheduled"

class SubscriptionStatus(enum.Enum):
    inactive = "inactive"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"

class ServiceType(enum.Enum):
    emergency = "emergency"
    leak = "leak"
    drain = "drain"
    toilet = "toilet"
    faucet = "faucet"
    sink = "sink"
    disposal = "disposal"
    water_heater = "water_heater"
    sewer = "sewer"
    repiping = "repiping"
    gas_line = "gas_line"
    backflow = "backflow"
    waterproofing = "waterproofing"
    sump_pump = "sump_pump"
    commercial = "commercial"
    inspection = "inspection"
    maintenance = "maintenance"
    renovation = "renovation"
    other = "other"

class UrgencyType(enum.Enum):
    emergency = "emergency"
    today = "today"
    tomorrow = "tomorrow"
    this_week = "this_week" 
    next_week = "next_week"
    flexible = "flexible"

# User model (for local development without Supabase auth)
class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.plumber)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plumber = relationship("Plumber", back_populates="user", uselist=False, cascade="all, delete-orphan")

# Plumber model
class Plumber(Base):
    __tablename__ = 'plumbers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_name = Column(String, nullable=False)
    contact_name = Column(String)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    service_radius = Column(Integer, default=25)
    services_offered = Column(ARRAY(String))  # Will be converted to/from ServiceType enum
    license_number = Column(String)
    is_insured = Column(Boolean, default=False)
    latitude = Column(Float)
    longitude = Column(Float)
    is_active = Column(Boolean, default=True)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.inactive)
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    lead_credits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="plumber")
    claims = relationship("LeadClaim", back_populates="plumber", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Plumber {self.company_name}>"
    
    def add_lead_credits(self, count):
        """Add lead credits to the plumber's account."""
        self.lead_credits += count
        return True
    
    def use_lead_credit(self):
        """Use a lead credit when claiming a lead."""
        if self.lead_credits <= 0:
            return False
        self.lead_credits -= 1
        return True

# Lead model
class Lead(Base):
    __tablename__ = 'leads'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    problem_description = Column(Text)
    service_needed = Column(ARRAY(String))  # Will be converted to/from ServiceType enum
    urgency = Column(Enum(UrgencyType), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(Enum(LeadStatus), default=LeadStatus.new)
    reference_code = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claims = relationship("LeadClaim", back_populates="lead", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lead {self.id} - {self.customer_name}>"
    
    @classmethod
    def update_status(cls, lead_id, new_status):
        """Update the status of a lead."""
        session = db.session
        lead = session.query(cls).filter_by(id=lead_id).first()
        if lead:
            lead.status = LeadStatus(new_status)
            session.commit()
            return lead
        return None

# Lead Claim model
class LeadClaim(Base):
    __tablename__ = 'lead_claims'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey('leads.id', ondelete='CASCADE'), nullable=False)
    plumber_id = Column(UUID(as_uuid=True), ForeignKey('plumbers.id', ondelete='CASCADE'), nullable=False)
    claimed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.new)
    contact_status = Column(Enum(ContactStatus))
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="claims")
    plumber = relationship("Plumber", back_populates="claims")
    
    def __repr__(self):
        return f"<LeadClaim {self.id}>"
    
    def update_status(self, new_status, contact_status=None, notes=None):
        """Update the status of a lead claim."""
        self.status = ClaimStatus(new_status)
        if contact_status:
            self.contact_status = ContactStatus(contact_status)
        if notes:
            self.notes = notes
        return True

# Settings model
class Setting(Base):
    __tablename__ = 'settings'
    
    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
    description = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    
    def __repr__(self):
        return f"<Setting {self.key}>"

def init_db(app):
    """Initialize the database with the app."""
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        # Import here to avoid circular imports
        from app.models.base import Base
        # This doesn't actually create the tables if using Supabase
        # We'll rely on our reset_db.py script instead
        # Base.metadata.create_all(db.engine)
        
    return db
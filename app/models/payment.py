from datetime import datetime
from app import db
import uuid

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    lead_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('leads.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    payment_method = db.Column(db.String(50), nullable=False)
    payment_processor = db.Column(db.String(50), nullable=False)
    processor_payment_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    payment_intent_id = db.Column(db.String(100))
    client_secret = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    refunded_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'lead_id': str(self.lead_id),
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_processor': self.payment_processor,
            'processor_payment_id': self.processor_payment_id,
            'status': self.status,
            'payment_intent_id': self.payment_intent_id,
            'client_secret': self.client_secret,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None
        }
    
    def mark_completed(self):
        """Mark payment as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error_message):
        """Mark payment as failed"""
        self.status = 'failed'
        self.error_message = error_message
    
    def mark_refunded(self):
        """Mark payment as refunded"""
        self.status = 'refunded'
        self.refunded_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Payment {self.id}>' 
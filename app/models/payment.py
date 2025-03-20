from datetime import datetime
from app import db
import uuid

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    lead_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('leads.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    payment_method = db.Column(db.String(50), nullable=False)
    payment_processor = db.Column(db.String(50), nullable=False)
    processor_payment_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    refund_reason = db.Column(db.Text)
    refunded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lead_id': str(self.lead_id),  # Convert UUID to string
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_processor': self.payment_processor,
            'processor_payment_id': self.processor_payment_id,
            'status': self.status,
            'refund_reason': self.refund_reason,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def mark_as_completed(self, processor_payment_id=None):
        """Mark payment as completed"""
        self.status = 'completed'
        if processor_payment_id:
            self.processor_payment_id = processor_payment_id
    
    def mark_as_failed(self):
        """Mark payment as failed"""
        self.status = 'failed'
    
    def refund(self, reason):
        """Mark payment as refunded"""
        self.status = 'refunded'
        self.refund_reason = reason
        self.refunded_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Payment {self.id}: {self.amount} {self.currency}>' 
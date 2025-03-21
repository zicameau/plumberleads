from datetime import datetime
from app import db
from app.models.lead import Lead
from app.models.payment import Payment
from app import create_app

def release_expired_reservations():
    """Release leads that have been reserved for more than 60 minutes"""
    app = create_app()
    
    with app.app_context():
        # Get all reserved leads
        reserved_leads = Lead.query.filter_by(status='reserved').all()
        
        for lead in reserved_leads:
            if lead.is_reservation_expired():
                # Get the associated payment
                payment = Payment.query.filter_by(
                    lead_id=lead.id,
                    user_id=lead.reserved_by_id
                ).first()
                
                if payment:
                    # Mark payment as failed
                    payment.mark_failed('Reservation expired')
                
                # Release the lead
                lead.release()
        
        # Commit all changes
        db.session.commit()

if __name__ == '__main__':
    release_expired_reservations() 
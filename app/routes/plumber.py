from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.lead import Lead
from app.models.user import User
from app import db
import json
from datetime import datetime
from sqlalchemy import func
import math

plumber = Blueprint('plumber', __name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points using the Haversine formula."""
    R = 3959.87433  # Earth's radius in miles

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c

    return distance

@plumber.route('/plumber/home')
@login_required
def plumber_home():
    if not current_user.is_verified:
        flash('Please verify your account to access the plumber dashboard.', 'warning')
        return redirect(url_for('main.index'))
    
    # Get nearby leads within the plumber's service radius
    nearby_leads = Lead.query.filter(
        Lead.is_claimed == False,
        Lead.latitude.isnot(None),
        Lead.longitude.isnot(None)
    ).all()
    
    # Filter leads by distance
    filtered_leads = []
    for lead in nearby_leads:
        distance = calculate_distance(
            current_user.latitude, current_user.longitude,
            lead.latitude, lead.longitude
        )
        if distance <= current_user.service_radius:
            filtered_leads.append(lead)
    
    # Get claimed leads
    claimed_leads = Lead.query.filter_by(
        plumber_id=current_user.id,
        is_claimed=True
    ).order_by(Lead.claimed_at.desc()).all()
    
    return render_template('plumber/home.html',
                         nearby_leads=filtered_leads,
                         claimed_leads=claimed_leads)

@plumber.route('/plumber/nearby-leads')
@login_required
def nearby_leads():
    if not current_user.is_verified:
        return jsonify({'error': 'Please verify your account'}), 403
    
    # Get all unclaimed leads with coordinates
    leads = Lead.query.filter(
        Lead.is_claimed == False,
        Lead.latitude.isnot(None),
        Lead.longitude.isnot(None)
    ).all()
    
    # Filter and format leads by distance
    nearby_leads = []
    for lead in leads:
        distance = calculate_distance(
            current_user.latitude, current_user.longitude,
            lead.latitude, lead.longitude
        )
        if distance <= current_user.service_radius:
            nearby_leads.append({
                'id': str(lead.id),
                'title': lead.title,
                'description': lead.description,
                'address': lead.address,
                'city': lead.city,
                'state': lead.state,
                'zip_code': lead.zip_code,
                'price': lead.price,
                'distance': round(distance, 2),
                'created_at': lead.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return jsonify(nearby_leads)

@plumber.route('/plumber/claimed-leads')
@login_required
def claimed_leads():
    if not current_user.is_verified:
        return jsonify({'error': 'Please verify your account'}), 403
    
    leads = Lead.query.filter_by(
        plumber_id=current_user.id,
        is_claimed=True
    ).order_by(Lead.claimed_at.desc()).all()
    
    return jsonify([{
        'id': str(lead.id),
        'title': lead.title,
        'status': lead.status,
        'claimed_at': lead.claimed_at.strftime('%Y-%m-%d %H:%M:%S'),
        'price': lead.price
    } for lead in leads])

@plumber.route('/plumber/claim-lead/<uuid:lead_id>', methods=['POST'])
@login_required
def claim_lead(lead_id):
    if not current_user.is_verified:
        return jsonify({'error': 'Please verify your account'}), 403
    
    lead = Lead.query.get_or_404(lead_id)
    
    if lead.is_claimed:
        return jsonify({'error': 'This lead has already been claimed'}), 400
    
    # Check if the lead is within the plumber's service radius
    distance = calculate_distance(
        current_user.latitude, current_user.longitude,
        lead.latitude, lead.longitude
    )
    
    if distance > current_user.service_radius:
        return jsonify({'error': 'This lead is outside your service area'}), 400
    
    # Claim the lead
    lead.is_claimed = True
    lead.claimed_at = datetime.utcnow()
    lead.plumber_id = current_user.id
    lead.status = 'new'
    
    db.session.commit()
    
    return jsonify({'message': 'Lead claimed successfully'})

@plumber.route('/plumber/update-lead-status/<uuid:lead_id>', methods=['POST'])
@login_required
def update_lead_status(lead_id):
    if not current_user.is_verified:
        return jsonify({'error': 'Please verify your account'}), 403
    
    lead = Lead.query.get_or_404(lead_id)
    
    if lead.plumber_id != current_user.id:
        return jsonify({'error': 'You do not have permission to update this lead'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    notes = data.get('notes')
    
    if new_status not in ['new', 'contacted', 'scheduled', 'completed', 'closed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    lead.status = new_status
    if notes:
        lead.notes = notes
    
    db.session.commit()
    
    return jsonify({'message': 'Lead status updated successfully'}) 
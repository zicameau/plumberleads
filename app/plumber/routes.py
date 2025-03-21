from flask import render_template, redirect, url_for, flash, request, session
from app.plumber import bp
from app.models.lead import Lead
from app.models.user import User
from sqlalchemy import func
from app import db
import json
from app.utils.pricing import calculate_lead_price

@bp.route('/dashboard')
def dashboard():
    if not session.get('user'):
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found. Please try logging in again.', 'error')
        return redirect(url_for('auth.login'))
    
    if not user.latitude or not user.longitude:
        flash('Please update your location information in your profile to view nearby leads.', 'warning')
        nearby_leads = []
    else:
        # Get nearby leads
        nearby_leads = Lead.query.filter(
            Lead.status == 'available',
            Lead.latitude.isnot(None),
            Lead.longitude.isnot(None),
            func.earth_distance(
                func.ll_to_earth(Lead.latitude, Lead.longitude),
                func.ll_to_earth(user.latitude, user.longitude)
            ) <= user.service_radius * 1609.34  # Convert miles to meters
        ).all()
    
    # Get user's reserved leads
    reserved_leads = Lead.query.filter_by(
        reserved_by_id=user_id,
        status='reserved'
    ).all()
    
    return render_template('plumber/dashboard.html',
                         user=user,
                         reserved_leads=reserved_leads,
                         nearby_leads=nearby_leads,
                         calculate_lead_price=calculate_lead_price)

@bp.route('/reserved-leads')
def reserved_leads():
    if not session.get('user'):
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['id']
    leads = Lead.query.filter_by(
        reserved_by_id=user_id,
        status='reserved'  # Only get reserved leads
    ).all()
    return render_template('plumber/reserved_leads.html', leads=leads)

@bp.route('/nearby-leads')
def nearby_leads():
    if not session.get('user'):
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    if not user.latitude or not user.longitude:
        flash('Please update your location information in your profile to view nearby leads.', 'warning')
        leads = []
    else:
        # Calculate distance in the subquery
        distance_calc = func.earth_distance(
            func.ll_to_earth(Lead.latitude, Lead.longitude),
            func.ll_to_earth(user.latitude, user.longitude)
        ).label('distance_meters')

        # Get nearby leads with distance calculation
        leads_query = db.session.query(
            Lead,
            distance_calc
        ).filter(
            Lead.status == 'available',
            Lead.latitude.isnot(None),
            Lead.longitude.isnot(None),
            distance_calc <= user.service_radius * 1609.34  # Convert miles to meters
        ).order_by(distance_calc)  # Sort by nearest first
        
        # Execute query and process results
        leads = []
        for lead, distance_meters in leads_query.all():
            lead.distance = distance_meters / 1609.34  # Convert meters to miles
            leads.append(lead)
    
    return render_template('plumber/nearby_leads.html',
                         leads=leads,
                         calculate_lead_price=calculate_lead_price) 
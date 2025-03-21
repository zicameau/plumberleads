from flask import render_template, redirect, url_for, flash, request, session
from app.plumber import bp
from app.models.lead import Lead
from app.models.user import User
from sqlalchemy import func
import json

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
    
    # Get user's claimed leads
    claimed_leads = Lead.query.filter_by(reserved_by_id=user_id).all()
    
    return render_template('plumber/dashboard.html',
                         user=user,
                         claimed_leads=claimed_leads,
                         nearby_leads=nearby_leads)

@bp.route('/claimed-leads')
def claimed_leads():
    if not session.get('user'):
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['id']
    leads = Lead.query.filter_by(reserved_by_id=user_id).all()
    return render_template('plumber/claimed_leads.html', leads=leads)

@bp.route('/nearby-leads')
def nearby_leads():
    if not session.get('user'):
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found. Please try logging in again.', 'error')
        return redirect(url_for('auth.login'))
    
    if not user.latitude or not user.longitude:
        flash('Please update your location information in your profile to view nearby leads.', 'warning')
        leads = []
    else:
        # Get nearby leads within service radius
        leads = Lead.query.filter(
            Lead.status == 'available',
            Lead.latitude.isnot(None),
            Lead.longitude.isnot(None),
            func.earth_distance(
                func.ll_to_earth(Lead.latitude, Lead.longitude),
                func.ll_to_earth(user.latitude, user.longitude)
            ) <= user.service_radius * 1609.34  # Convert miles to meters
        ).all()
    
    return render_template('plumber/nearby_leads.html', leads=leads, user=user) 
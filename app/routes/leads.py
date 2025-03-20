from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.lead import Lead
from app import db

leads = Blueprint('leads', __name__)

@leads.route('/leads')
def available():
    """Display available leads for plumbers"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get all unclaimed leads
    query = Lead.query.filter_by(is_claimed=False)
    
    # Apply filters if provided
    service_type = request.args.get('service_type')
    if service_type:
        query = query.filter_by(service_type=service_type)
    
    urgency = request.args.get('urgency')
    if urgency:
        query = query.filter_by(urgency=urgency)
    
    # Apply sorting
    sort_by = request.args.get('sort', 'created_at')
    if sort_by == 'price_asc':
        query = query.order_by(Lead.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Lead.price.desc())
    else:
        query = query.order_by(Lead.created_at.desc())
    
    # Paginate results
    leads_page = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('leads/list.html', 
                         leads=leads_page.items,
                         total=leads_page.total,
                         pages=leads_page.pages,
                         current_page=page)

@leads.route('/leads/submit', methods=['GET', 'POST'])
def submit():
    """Handle lead submission form"""
    if request.method == 'POST':
        # Handle form submission
        # This will be implemented later
        pass
    
    return render_template('leads/submit.html') 
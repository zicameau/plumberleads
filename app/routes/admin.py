# app/routes/admin.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, current_app
from app.services.auth_service import token_required, admin_required
from app.models.lead import Lead
from app.models.plumber import Plumber
from app.models.lead_claim import LeadClaim
import logging

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
@token_required
@admin_required
def dashboard():
    """Admin dashboard showing overview and stats."""
    try:
        # Get basic stats
        from app.services.lead_service import get_lead_statistics
        
        # Get counts from database
        lead_count = Lead.count()
        plumber_count = Plumber.count()
        active_plumber_count = Plumber.count({"subscription_status": "active"})
        claimed_lead_count = Lead.count({"status": "claimed"})
        completed_lead_count = Lead.count({"status": "completed"})
        
        # Calculate percentage of claimed leads
        claimed_percentage = 0
        if lead_count > 0:
            claimed_percentage = (claimed_lead_count / lead_count) * 100
        
        # Calculate completion rate
        completion_rate = 0
        if claimed_lead_count > 0:
            completion_rate = (completed_lead_count / claimed_lead_count) * 100
            
        # Get recent leads
        recent_leads = Lead.get_recent(limit=5)
        
        # Get recent plumber signups
        recent_plumbers = Plumber.get_recent(limit=5)
        
        return render_template('admin/dashboard.html',
                             lead_count=lead_count,
                             plumber_count=plumber_count,
                             active_plumber_count=active_plumber_count,
                             claimed_percentage=claimed_percentage,
                             completion_rate=completion_rate,
                             recent_leads=recent_leads,
                             recent_plumbers=recent_plumbers)
    
    except Exception as e:
        current_app.logger.error(f"Error in admin dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('admin/dashboard.html', error=True)

@admin_bp.route('/leads', methods=['GET'])
@token_required
@admin_required
def manage_leads():
    """View and manage all leads."""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        # Get leads based on filter
        if status_filter and status_filter != 'all':
            leads = Lead.find_by_status(
                status=status_filter,
                limit=per_page,
                offset=offset
            )
            total_count = Lead.count({"status": status_filter})
        else:
            leads = Lead.get_all(
                limit=per_page,
                offset=offset
            )
            total_count = Lead.count()
        
        # Calculate total pages
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('admin/leads.html',
                             leads=leads,
                             page=page,
                             total_pages=total_pages,
                             status_filter=status_filter)
    
    except Exception as e:
        current_app.logger.error(f"Error in manage_leads: {str(e)}")
        flash('An error occurred while loading leads.', 'error')
        return render_template('admin/leads.html', error=True)

@admin_bp.route('/leads/<lead_id>', methods=['GET'])
@token_required
@admin_required
def view_lead(lead_id):
    """View details for a specific lead."""
    try:
        # Get lead
        lead = Lead.get_by_id(lead_id)
        
        if not lead:
            flash('Lead not found.', 'error')
            return redirect(url_for('admin.manage_leads'))
        
        # Get claims for this lead
        claims = LeadClaim.get_by_lead(lead_id)
        
        # Get plumber details for each claim
        claimed_by = []
        for claim in claims:
            plumber = Plumber.get_by_id(claim.plumber_id)
            if plumber:
                claimed_by.append({
                    'plumber': plumber,
                    'claim': claim
                })
        
        return render_template('admin/lead_detail.html',
                             lead=lead,
                             claimed_by=claimed_by)
    
    except Exception as e:
        current_app.logger.error(f"Error in view_lead: {str(e)}")
        flash('An error occurred while loading lead details.', 'error')
        return redirect(url_for('admin.manage_leads'))

@admin_bp.route('/plumbers', methods=['GET'])
@token_required
@admin_required
def manage_plumbers():
    """View and manage all plumbers."""
    try:
        # Get filter parameters
        subscription_filter = request.args.get('subscription', '')
        page = int(request.args.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        # Get plumbers based on filter
        if subscription_filter and subscription_filter != 'all':
            plumbers = Plumber.find_by_subscription_status(
                status=subscription_filter,
                limit=per_page,
                offset=offset
            )
            total_count = Plumber.count({"subscription_status": subscription_filter})
        else:
            plumbers = Plumber.get_all(
                limit=per_page,
                offset=offset
            )
            total_count = Plumber.count()
        
        # Calculate total pages
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('admin/plumbers.html',
                             plumbers=plumbers,
                             page=page,
                             total_pages=total_pages,
                             subscription_filter=subscription_filter)
    
    except Exception as e:
        current_app.logger.error(f"Error in manage_plumbers: {str(e)}")
        flash('An error occurred while loading plumbers.', 'error')
        return render_template('admin/plumbers.html', error=True)

@admin_bp.route('/plumbers/<plumber_id>', methods=['GET'])
@token_required
@admin_required
def view_plumber(plumber_id):
    """View details for a specific plumber."""
    try:
        # Get plumber
        plumber = Plumber.get_by_id(plumber_id)
        
        if not plumber:
            flash('Plumber not found.', 'error')
            return redirect(url_for('admin.manage_plumbers'))
        
        # Get subscription details if available
        subscription_details = None
        if plumber.subscription_status == 'active' and plumber.stripe_subscription_id:
            from app.services.payment_service import get_stripe
            stripe = get_stripe()
            subscription_details = stripe.Subscription.retrieve(plumber.stripe_subscription_id)
            
        # Get recent lead claims by this plumber
        claims = LeadClaim.get_by_plumber(
            plumber_id=plumber_id,
            limit=10
        )
        
        # Get lead details for each claim
        claimed_leads = []
        for claim in claims:
            lead = Lead.get_by_id(claim.lead_id)
            if lead:
                claimed_leads.append({
                    'lead': lead,
                    'claim': claim
                })
        
        return render_template('admin/plumber_detail.html',
                             plumber=plumber,
                             subscription=subscription_details,
                             claimed_leads=claimed_leads)
    
    except Exception as e:
        current_app.logger.error(f"Error in view_plumber: {str(e)}")
        flash('An error occurred while loading plumber details.', 'error')
        return redirect(url_for('admin.manage_plumbers'))

@admin_bp.route('/plumbers/<plumber_id>/add-credits', methods=['POST'])
@token_required
@admin_required
def add_lead_credits(plumber_id):
    """Add lead credits to a plumber's account."""
    try:
        # Get plumber
        plumber = Plumber.get_by_id(plumber_id)
        
        if not plumber:
            return jsonify({'success': False, 'error': 'Plumber not found'})
        
        # Get number of credits to add
        try:
            credit_count = int(request.form.get('credit_count', 0))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid credit count'})
            
        if credit_count <= 0:
            return jsonify({'success': False, 'error': 'Credit count must be positive'})
        
        # Add credits
        if plumber.add_lead_credits(credit_count):
            # Send notification
            from app.services.notification_service import send_lead_credit_purchase_confirmation
            send_lead_credit_purchase_confirmation(plumber, credit_count, 0)  # $0 since admin added them
            
            return jsonify({
                'success': True,
                'message': f'Added {credit_count} lead credits',
                'new_balance': plumber.lead_credits
            })
        
        return jsonify({'success': False, 'error': 'Failed to add lead credits'})
        
    except Exception as e:
        current_app.logger.error(f"Error in add_lead_credits: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/reports', methods=['GET'])
@token_required
@admin_required
def reports():
    """Generate various reports."""
    try:
        # Get report type
        report_type = request.args.get('type', 'leads')
        
        # Get date range
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Default to last 30 days
        
        if request.args.get('start_date'):
            try:
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            except ValueError:
                pass
                
        if request.args.get('end_date'):
            try:
                end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
                # Set to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
        
        # Generate the requested report
        if report_type == 'leads':
            # Lead generation report
            report_data = Lead.get_report_by_date_range(start_date, end_date)
            
        elif report_type == 'claims':
            # Lead claims report
            report_data = LeadClaim.get_report_by_date_range(start_date, end_date)
            
        elif report_type == 'revenue':
            # Revenue report
            from app.services.payment_service import get_stripe
            stripe = get_stripe()
            
            # Query Stripe for payments in date range
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            # Get subscription invoices
            invoices = stripe.Invoice.list(
                created={
                    'gte': start_timestamp,
                    'lte': end_timestamp
                },
                status='paid',
                limit=100
            )
            
            # Get one-time payments
            charges = stripe.Charge.list(
                created={
                    'gte': start_timestamp,
                    'lte': end_timestamp
                },
                status='succeeded',
                limit=100
            )
            
            # Combine and process data
            report_data = {
                'subscription_revenue': sum(invoice.amount_paid for invoice in invoices),
                'lead_credit_revenue': sum(charge.amount for charge in charges if charge.metadata.get('type') == 'lead_credit_purchase'),
                'invoices': invoices.data,
                'charges': charges.data
            }
            
        elif report_type == 'plumbers':
            # Plumber activity report
            report_data = Plumber.get_activity_report(start_date, end_date)
            
        else:
            report_data = {}
        
        return render_template('admin/reports.html',
                             report_type=report_type,
                             start_date=start_date.strftime('%Y-%m-%d'),
                             end_date=end_date.strftime('%Y-%m-%d'),
                             report_data=report_data)
    
    except Exception as e:
        current_app.logger.error(f"Error in reports: {str(e)}")
        flash('An error occurred while generating the report.', 'error')
        return render_template('admin/reports.html', error=True)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@token_required
@admin_required
def settings():
    """Manage platform settings."""
    try:
        if request.method == 'POST':
            # Update settings
            updated_settings = {
                'LEAD_RADIUS_MILES': int(request.form.get('lead_radius', 25)),
                'LEAD_PRICE': float(request.form.get('lead_price', 10.00)),
                'APP_NAME': request.form.get('app_name', 'Plumber Leads'),
                'MONTHLY_SUBSCRIPTION_PRICE_ID': request.form.get('subscription_price_id')
            }
            
            # Update configuration in database
            # In a real application, you'd store these in a settings table
            # For simplicity, we'll just update the current app config
            for key, value in updated_settings.items():
                current_app.config[key] = value
            
            flash('Settings updated successfully.', 'success')
            
        # Get current settings
        current_settings = {
            'lead_radius': current_app.config.get('LEAD_RADIUS_MILES', 25),
            'lead_price': current_app.config.get('LEAD_PRICE', 10.00),
            'app_name': current_app.config.get('APP_NAME', 'Plumber Leads'),
            'subscription_price_id': current_app.config.get('MONTHLY_SUBSCRIPTION_PRICE_ID', '')
        }
        
        return render_template('admin/settings.html', settings=current_settings)
    
    except Exception as e:
        current_app.logger.error(f"Error in settings: {str(e)}")
        flash('An error occurred while managing settings.', 'error')
        return render_template('admin/settings.html', error=True)

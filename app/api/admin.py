from flask import jsonify, request, current_app
from flask_login import current_user, login_required
from app import db
from app.api import bp
from app.models.user import User
from app.models.lead import Lead
from app.models.payment import Payment
from datetime import datetime, timedelta
import json
import os

# Admin-only middleware
def admin_required(func):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return func(*args, **kwargs)
    decorated_function.__name__ = func.__name__
    return login_required(decorated_function)

# Admin dashboard stats
@bp.route('/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    # Time period filter (default: last 30 days)
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # User stats
    total_users = User.query.filter_by(is_admin=False).count()
    active_users = User.query.filter_by(is_admin=False, is_active=True).count()
    verified_users = User.query.filter_by(is_admin=False, is_verified=True).count()
    new_users = User.query.filter(User.created_at >= start_date, User.is_admin==False).count()
    
    # Lead stats
    total_leads = Lead.query.count()
    new_leads = Lead.query.filter(Lead.created_at >= start_date).count()
    claimed_leads = Lead.query.filter_by(is_claimed=True).count()
    claimed_percentage = (claimed_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Payment stats
    completed_payments = Payment.query.filter_by(status='completed').count()
    total_revenue = db.session.query(db.func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0
    recent_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status=='completed', 
        Payment.created_at >= start_date
    ).scalar() or 0
    
    # Service type distribution
    service_types = db.session.query(
        Lead.service_type, 
        db.func.count(Lead.id)
    ).group_by(Lead.service_type).all()
    
    service_type_stats = {service_type: count for service_type, count in service_types}
    
    # Geographic distribution (by state)
    geographic_stats = db.session.query(
        Lead.state, 
        db.func.count(Lead.id)
    ).group_by(Lead.state).all()
    
    state_distribution = {state: count for state, count in geographic_stats}
    
    return jsonify({
        'user_stats': {
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'new_users': new_users,
            'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0
        },
        'lead_stats': {
            'total_leads': total_leads,
            'new_leads': new_leads,
            'claimed_leads': claimed_leads,
            'claimed_percentage': claimed_percentage,
            'service_type_distribution': service_type_stats
        },
        'payment_stats': {
            'completed_payments': completed_payments,
            'total_revenue': total_revenue,
            'recent_revenue': recent_revenue,
            'average_payment': (total_revenue / completed_payments) if completed_payments > 0 else 0
        },
        'geographic_stats': {
            'state_distribution': state_distribution
        },
        'time_period': {
            'days': days,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat()
        }
    })

# Get system logs
@bp.route('/admin/logs', methods=['GET'])
@admin_required
def get_logs():
    # Parse query parameters
    log_type = request.args.get('type', 'application')  # application, access, error
    lines = min(request.args.get('lines', 100, type=int), 1000)  # Max 1000 lines
    
    # Define log file paths
    log_files = {
        'application': current_app.config.get('APPLICATION_LOG', '/var/log/plumberleads/application.log'),
        'access': current_app.config.get('ACCESS_LOG', '/var/log/plumberleads/access.log'),
        'error': current_app.config.get('ERROR_LOG', '/var/log/plumberleads/error.log')
    }
    
    # Get the requested log file
    log_file = log_files.get(log_type)
    
    # Check if we're in local dev mode
    if os.environ.get('LOCAL_DEV') == 'True':
        # Use local log files for development
        log_file = f"logs/{log_type}.log"
    
    try:
        # Check if file exists
        if not os.path.exists(log_file):
            return jsonify({
                'error': f'Log file {log_file} does not exist',
                'log_type': log_type,
                'lines': []
            }), 404
        
        # Read the last N lines (using tail command or file reading)
        with open(log_file, 'r') as f:
            # Read all lines and take the last N
            all_lines = f.readlines()
            log_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return jsonify({
            'log_type': log_type,
            'lines': log_lines,
            'total_lines': len(log_lines)
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'log_type': log_type,
            'lines': []
        }), 500

# Get system configuration
@bp.route('/admin/config', methods=['GET'])
@admin_required
def get_config():
    # Only return non-sensitive configuration
    safe_config = {
        'FLASK_ENV': current_app.config.get('FLASK_ENV', 'production'),
        'SERVER_NAME': current_app.config.get('SERVER_NAME'),
        'APPLICATION_ROOT': current_app.config.get('APPLICATION_ROOT'),
        'PREFERRED_URL_SCHEME': current_app.config.get('PREFERRED_URL_SCHEME'),
        'LEAD_CLAIM_PERCENTAGE': current_app.config.get('LEAD_CLAIM_PERCENTAGE'),
        'DEFAULT_CURRENCY': current_app.config.get('DEFAULT_CURRENCY'),
        'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
        'MAIL_PORT': current_app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': current_app.config.get('MAIL_USE_SSL'),
        'ADMIN_EMAIL': current_app.config.get('ADMIN_EMAIL'),
        'DATABASE_TYPE': current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split('://')[0] if '://' in current_app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'unknown'
    }
    
    return jsonify(safe_config)

# Update system configuration
@bp.route('/admin/config', methods=['PUT'])
@admin_required
def update_config():
    data = request.get_json() or {}
    
    # List of allowed configuration options to update
    allowed_config_options = [
        'LEAD_CLAIM_PERCENTAGE',
        'DEFAULT_CURRENCY',
        'MAIL_SERVER',
        'MAIL_PORT',
        'MAIL_USE_TLS',
        'MAIL_USE_SSL',
        'ADMIN_EMAIL'
    ]
    
    updated_config = {}
    
    for key, value in data.items():
        if key in allowed_config_options:
            # Update the current application config
            current_app.config[key] = value
            updated_config[key] = value
            
            # TODO: Persist this configuration to a file or database
            # This is just updating runtime config, will be lost on restart
    
    if not updated_config:
        return jsonify({'error': 'No valid configuration options provided'}), 400
    
    return jsonify({
        'message': 'Configuration updated successfully',
        'updated_config': updated_config
    })

# Get user activity report
@bp.route('/admin/reports/user-activity', methods=['GET'])
@admin_required
def user_activity_report():
    # Parse query parameters
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get active users who have claimed at least one lead
    active_users = db.session.query(User).join(
        Lead, User.id == Lead.plumber_id
    ).filter(
        Lead.claimed_at >= start_date,
        User.is_admin == False
    ).distinct().all()
    
    # Format the report data
    report_data = []
    
    for user in active_users:
        # Get leads claimed by this user in the time period
        leads_claimed = Lead.query.filter(
            Lead.plumber_id == user.id,
            Lead.claimed_at >= start_date
        ).all()
        
        # Get payments made by this user in the time period
        payments = Payment.query.filter(
            Payment.user_id == user.id,
            Payment.created_at >= start_date
        ).all()
        
        # Calculate total spent
        total_spent = sum(p.amount for p in payments if p.status == 'completed')
        
        report_data.append({
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'company_name': user.company_name,
            'is_verified': user.is_verified,
            'is_active': user.is_active,
            'leads_claimed': len(leads_claimed),
            'total_spent': total_spent,
            'avg_lead_cost': total_spent / len(leads_claimed) if leads_claimed else 0,
            'join_date': user.created_at.isoformat()
        })
    
    # Sort by number of leads claimed (descending)
    report_data.sort(key=lambda x: x['leads_claimed'], reverse=True)
    
    return jsonify({
        'report': 'user-activity',
        'time_period': {
            'days': days,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat()
        },
        'active_users_count': len(report_data),
        'data': report_data
    })

# Get lead conversion report
@bp.route('/admin/reports/lead-conversion', methods=['GET'])
@admin_required
def lead_conversion_report():
    # Parse query parameters
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all leads in the time period
    leads = Lead.query.filter(Lead.created_at >= start_date).all()
    
    # Calculate conversion metrics
    total_leads = len(leads)
    claimed_leads = sum(1 for lead in leads if lead.is_claimed)
    conversion_rate = (claimed_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Group leads by service type
    service_type_data = {}
    for lead in leads:
        service_type = lead.service_type
        if service_type not in service_type_data:
            service_type_data[service_type] = {
                'total': 0,
                'claimed': 0,
                'conversion_rate': 0
            }
        
        service_type_data[service_type]['total'] += 1
        if lead.is_claimed:
            service_type_data[service_type]['claimed'] += 1
    
    # Calculate conversion rates for each service type
    for service_type in service_type_data:
        total = service_type_data[service_type]['total']
        claimed = service_type_data[service_type]['claimed']
        conversion_rate = (claimed / total * 100) if total > 0 else 0
        service_type_data[service_type]['conversion_rate'] = conversion_rate
    
    # Calculate time to claim
    time_to_claim_data = []
    for lead in leads:
        if lead.is_claimed and lead.claimed_at:
            # Calculate time difference in hours
            time_diff = lead.claimed_at - lead.created_at
            hours_to_claim = time_diff.total_seconds() / 3600
            
            time_to_claim_data.append({
                'lead_id': lead.id,
                'created_at': lead.created_at.isoformat(),
                'claimed_at': lead.claimed_at.isoformat(),
                'hours_to_claim': hours_to_claim
            })
    
    # Calculate average time to claim
    avg_hours_to_claim = 0
    if time_to_claim_data:
        avg_hours_to_claim = sum(item['hours_to_claim'] for item in time_to_claim_data) / len(time_to_claim_data)
    
    return jsonify({
        'report': 'lead-conversion',
        'time_period': {
            'days': days,
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat()
        },
        'total_leads': total_leads,
        'claimed_leads': claimed_leads,
        'overall_conversion_rate': conversion_rate,
        'service_type_conversion': service_type_data,
        'avg_hours_to_claim': avg_hours_to_claim,
        'time_to_claim_data': time_to_claim_data
    }) 
import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, g, jsonify, session, flash, redirect, url_for
from app.services.supabase import init_supabase, get_supabase
from .mock.supabase_mock import SupabaseMock
import requests

# Get the auth logger
logger = logging.getLogger('auth')

def init_admin_user():
    """Initialize admin user in Supabase if it doesn't exist."""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Default password for testing
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not admin_password and not current_app.config.get('TESTING', False):
        logger.warning("ADMIN_PASSWORD environment variable not set. Admin user will not be created.")
        return
    
    if not supabase_service_key and not current_app.config.get('TESTING', False):
        logger.warning("SUPABASE_SERVICE_KEY environment variable not set. Admin user will not be created.")
        return
    
    logger.info(f"Checking if admin user {admin_email} exists")
    
    try:
        # Create admin user in Supabase
        supabase = get_supabase()
        if current_app.config.get('TESTING', False):
            # In test mode, use the mock client's signup method
            auth_response = supabase.auth.sign_up({
                'email': admin_email,
                'password': admin_password,
                'options': {
                    'data': {
                        'role': 'admin'
                    }
                }
            })
        else:
            # Use admin API to create user in production
            headers = {
                'apikey': supabase_service_key,
                'Authorization': f'Bearer {supabase_service_key}',
                'Content-Type': 'application/json'
            }
            response = requests.post(
                f"{os.environ.get('SUPABASE_URL')}/auth/v1/admin/users",
                headers=headers,
                json={
                    'email': admin_email,
                    'password': admin_password,
                    'user_metadata': {'role': 'admin'},
                    'email_confirm': True,
                    'app_metadata': {'provider': 'email'}
                }
            )
            response.raise_for_status()
            
        logger.info(f"Admin user {admin_email} created successfully")
            
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        if current_app.config.get('TESTING', False):
            # In test mode, we can ignore this error as the user might already exist
            return
        raise

def signup(email, password, metadata=None):
    """Sign up a new user."""
    try:
        supabase = get_supabase()
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': metadata or {}
            }
        })
        
        if auth_response and auth_response.user:
            session['token'] = auth_response.session.access_token
            session['user'] = {
                'id': auth_response.user.id,
                'email': auth_response.user.email,
                'role': metadata.get('role', 'user') if metadata else 'user'
            }
            return auth_response
            
        return None
        
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        return None

def login(email, password):
    """Login user with email and password."""
    try:
        logger.info(f"Attempting login for {email}")
        supabase = get_supabase()
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if auth_response and auth_response.user:
            session['token'] = auth_response.session.access_token
            session['user'] = {
                'id': auth_response.user.id,
                'email': auth_response.user.email,
                'role': auth_response.user.user_metadata.get('role', 'user')
            }
            logger.info(f"Login successful for {email}")
            return auth_response
        
        logger.warning(f"Login failed for {email}")
        return None
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return None

def logout():
    """Log out a user using Supabase Auth."""
    logger.info("Logout requested")
    
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Sign out the user
        supabase.auth.sign_out()
        logger.info("User logged out successfully from Supabase Auth")
        
        return True
    except Exception as e:
        logger.warning(f"Error during logout: {str(e)}")
        return False

def reset_password_request(email):
    """Request a password reset via Supabase Auth."""
    logger.info(f"Password reset requested for {email}")
    
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Send password reset email
        supabase.auth.reset_password_for_email(email)
        logger.info(f"Password reset email sent to {email}")
        
        return True
    except Exception as e:
        logger.error(f"Error requesting password reset for {email}: {str(e)}", exc_info=True)
        return False

def token_required(f):
    """Decorator to require Supabase authentication for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        request_id = f"req-{datetime.utcnow().timestamp()}"
        
        # Get access token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning(f"[{request_id}] No token found for request to {request.path}")
            
            # For API routes, return JSON response
            if request.path.startswith('/api/'):
                return jsonify({'message': 'No token provided'}), 401
            
            # For web routes, redirect to login
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
            
        token = auth_header.split(' ')[1]
        
        try:
            # Get Supabase client
            supabase = get_supabase()
            
            # Verify token and get user info
            auth_response = supabase.auth.get_user(token)
            
            if not auth_response or not auth_response.user:
                raise Exception("Invalid token - user not found")
            
            # Set user info in Flask g object for access in the route
            user = auth_response.user
            user_metadata = user.user_metadata or {}
            
            # Get role from metadata or default to customer
            role = user_metadata.get('role', 'customer')
            
            # Log the user metadata for debugging
            logger.info(f"[{request_id}] User metadata: {user_metadata}")
            
            g.user = {
                'id': user.id,
                'email': user.email,
                'role': role
            }
            
            logger.info(f"[{request_id}] Successfully authenticated user {g.user['id']} with role {g.user.get('role')}")
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning(f"[{request_id}] Authentication error for request to {request.path}: {str(e)}")
            
            # For API routes, return JSON response
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Authentication failed'}), 401
            
            # For web routes, redirect to login
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
    
    return decorated

def admin_required(f):
    """Decorator to require an admin role for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        request_id = f"req-{datetime.utcnow().timestamp()}"
        
        # Check if user is set in g
        if not hasattr(g, 'user'):
            logger.warning(f"[{request_id}] Admin check failed: No authenticated user")
            return jsonify({'message': 'Authentication required'}), 401
        
        # Check if user has admin role
        if g.user.get('role') != 'admin':
            logger.warning(f"[{request_id}] Access denied: User {g.user.get('id')} with role {g.user.get('role')} attempted to access admin route {request.path}")
            return jsonify({'message': 'Admin role required'}), 403
        
        logger.info(f"[{request_id}] Admin access granted to {g.user.get('id')} for {request.path}")
        return f(*args, **kwargs)
    
    return decorated

def plumber_required(f):
    """Decorator to require a plumber role for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        request_id = f"req-{datetime.utcnow().timestamp()}"
        
        # Check if user is set in g
        if not hasattr(g, 'user'):
            logger.warning(f"[{request_id}] Plumber check failed: No authenticated user")
            return jsonify({'message': 'Authentication required'}), 401
        
        # Check if user has plumber role
        if g.user.get('role') != 'plumber':
            logger.warning(f"[{request_id}] Access denied: User {g.user.get('id')} with role {g.user.get('role')} attempted to access plumber route {request.path}")
            return jsonify({'message': 'Plumber role required'}), 403
        
        logger.info(f"[{request_id}] Plumber access granted to {g.user.get('id')} for {request.path}")
        return f(*args, **kwargs)
    
    return decorated
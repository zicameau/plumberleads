import os
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, g, jsonify, session, flash, redirect, url_for
from app.models.base import db, User, Plumber, UserRole
from app.services.supabase import init_supabase, get_supabase
from .mock.supabase_mock import SupabaseMock
import uuid
import requests
from app.models.plumber import Plumber

# Get the auth logger
logger = logging.getLogger('auth')

def init_admin_user():
    """Initialize admin user in Supabase and local database if it doesn't exist."""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not admin_password:
        logger.warning("ADMIN_PASSWORD environment variable not set. Admin user will not be created.")
        return
    
    if not supabase_service_key:
        logger.warning("SUPABASE_SERVICE_KEY environment variable not set. Admin user will not be created.")
        return
    
    logger.info(f"Checking if admin user {admin_email} exists")
    
    try:
        # Check if admin user exists in local database
        with current_app.app_context():
            admin_user = db.session.query(User).filter_by(email=admin_email).first()
            
            if not admin_user:
                logger.info(f"Admin user {admin_email} not found in local database, creating...")
                
                # Try to create admin user in Supabase if not in testing mode
                if not current_app.config.get('TESTING', False):
                    try:
                        # Use admin API to create user
                        headers = {
                            'apikey': supabase_service_key,
                            'Authorization': f'Bearer {supabase_service_key}',
                            'Content-Type': 'application/json'
                        }
                        
                        # First check if user exists
                        response = requests.get(
                            f"{current_app.config['SUPABASE_URL']}/auth/v1/admin/users",
                            headers=headers
                        )
                        
                        if response.status_code != 200:
                            raise Exception(f"Failed to get users: {response.text}")
                        
                        users = response.json()
                        existing_user = next((user for user in users if user['email'] == admin_email), None)
                        
                        if existing_user:
                            # Update existing user's metadata
                            user_id = existing_user['id']
                            response = requests.put(
                                f"{current_app.config['SUPABASE_URL']}/auth/v1/admin/users/{user_id}",
                                headers=headers,
                                json={
                                    "user_metadata": {
                                        "role": "admin",
                                        "name": "Admin User"
                                    }
                                }
                            )
                            
                            if response.status_code != 200:
                                raise Exception(f"Failed to update user metadata: {response.text}")
                            
                            admin_id = user_id
                            logger.info(f"Updated existing user {admin_email} with admin role")
                        else:
                            # Create new user with admin role
                            response = requests.post(
                                f"{current_app.config['SUPABASE_URL']}/auth/v1/admin/users",
                                headers=headers,
                                json={
                                    "email": admin_email,
                                    "password": admin_password,
                                    "email_confirm": True,
                                    "user_metadata": {
                                        "role": "admin",
                                        "name": "Admin User"
                                    }
                                }
                            )
                            
                            if response.status_code != 200:
                                raise Exception(f"Failed to create admin user: {response.text}")
                            
                            admin_id = response.json()['id']
                            logger.info(f"Created new admin user {admin_email} with ID {admin_id}")
                    except Exception as e:
                        logger.error(f"Error managing admin user in Supabase: {str(e)}", exc_info=True)
                        # Continue with local database creation even if Supabase fails
                        # Generate a valid UUID for admin user
                        admin_id = str(uuid.uuid4())
                else:
                    # For testing, use a fixed UUID
                    admin_id = '123e4567-e89b-12d3-a456-426614174000'  # Valid UUID format
                
                # Create admin user in local database
                admin_user = User(
                    id=admin_id,
                    email=admin_email,
                    role=UserRole.admin
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info(f"Admin user {admin_email} created in local database with ID {admin_id}")
            else:
                logger.info(f"Admin user {admin_email} already exists in local database")
    except Exception as e:
        logger.error(f"Error initializing admin user: {str(e)}", exc_info=True)

def sync_user_to_db(supabase_user):
    """Sync Supabase user to local database."""
    try:
        # Check if user exists
        user = User.query.filter_by(id=supabase_user.id).first()
        
        if not user:
            # Create new user
            user = User(
                id=supabase_user.id,
                email=supabase_user.email,
                role=UserRole(supabase_user.user_metadata.get('role', 'customer')),
                created_at=datetime.fromisoformat(supabase_user.created_at),
                updated_at=datetime.fromisoformat(supabase_user.updated_at)
            )
            db.session.add(user)
        else:
            # Update existing user
            user.email = supabase_user.email
            user.role = UserRole(supabase_user.user_metadata.get('role', user.role.value))
            user.updated_at = datetime.fromisoformat(supabase_user.updated_at)
        
        db.session.commit()
        return user
    except Exception as e:
        print(f"Error syncing user to database: {str(e)}")
        db.session.rollback()
        return None

def signup(email, password, user_metadata=None):
    """Register a new user with Supabase Auth and sync to local database."""
    try:
        # Register with Supabase Auth
        auth_response = get_supabase().auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': user_metadata
            }
        })
        
        if not auth_response.user:
            return None
            
        # Sync user to local database
        user = sync_user_to_db(auth_response.user)
        
        # If this is a plumber registration, create plumber profile
        if user and user.role == UserRole.plumber:
            plumber_data = {
                'user_id': user.id,
                'company_name': user_metadata.get('company_name', ''),
                'contact_name': user_metadata.get('contact_name', ''),
                'phone': user_metadata.get('phone', ''),
                'email': email
            }
            Plumber.create(plumber_data)
        
        return user
    except Exception as e:
        print(f"Error in signup: {str(e)}")
        return None

def login(email, password):
    """Login user with Supabase Auth and sync to local database."""
    try:
        # Login with Supabase Auth
        auth_response = get_supabase().auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if not auth_response.user:
            return None
            
        # Sync user to local database
        user = sync_user_to_db(auth_response.user)
        
        # If this is a plumber, ensure plumber profile exists
        if user and user.role == UserRole.plumber:
            plumber = Plumber.get_by_user_id(user.id)
            if not plumber:
                # Create basic plumber profile if it doesn't exist
                plumber_data = {
                    'user_id': user.id,
                    'company_name': '',
                    'contact_name': '',
                    'phone': '',
                    'email': email
                }
                Plumber.create(plumber_data)
        
        return user
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return None

def logout(token):
    """Log out a user by invalidating their token in Supabase Auth."""
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

def generate_token(payload, expires_delta=None):
    """Generate a JWT token."""
    now = datetime.utcnow()
    if not expires_delta:
        expires_delta = timedelta(days=1)
    payload_copy = payload.copy()
    exp = now + expires_delta
    payload_copy.update({"exp": exp, "iat": now, "sub": payload.get("id", "")})
    
    secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    token = jwt.encode(payload_copy, secret_key, algorithm='HS256')
    
    logger.info(f"Generated token for user {payload.get('id')} with role {payload.get('role')}")
    return token

def decode_token(token):
    """Decode a JWT token."""
    secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    try:
        return jwt.decode(
            token,
            secret_key,
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require a valid token for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        request_id = f"req-{datetime.utcnow().timestamp()}"
        
        # Get token from Authorization header or session
        token = None
        
        # Check Authorization header first
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # If no token in header, check session
        if not token and 'token' in session:
            token = session['token']
        
        if not token:
            logger.warning(f"[{request_id}] No token found for request to {request.path}")
            
            # For API routes, return JSON response
            if request.path.startswith('/api/'):
                return jsonify({'message': 'No token provided'}), 401
            
            # For web routes, redirect to login
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
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
            
            # Clear session
            session.clear()
            
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
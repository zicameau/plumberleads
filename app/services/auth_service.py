import os
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, g, jsonify, session, flash, redirect, url_for
from app.models.base import db, User, Plumber, UserRole
from supabase import create_client, Client
from .mock.supabase_mock import SupabaseMock

# Get the auth logger
logger = logging.getLogger('auth')

# Global variable to store Supabase client
_supabase_client = None

def init_supabase(url, key, testing=False):
    """Initialize the Supabase client."""
    global _supabase_client
    
    # Use mock client for testing
    if testing:
        logger.info("Using mock Supabase client for testing")
        _supabase_client = SupabaseMock()
        return _supabase_client
        
    try:
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
        raise

def get_supabase():
    """Get the Supabase client instance."""
    if not _supabase_client:
        raise RuntimeError("Supabase client not initialized")
    return _supabase_client

def init_admin_user():
    """Initialize admin user in Supabase and local database if it doesn't exist."""
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if not admin_password:
        logger.warning("ADMIN_PASSWORD environment variable not set. Admin user will not be created.")
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
                        supabase = get_supabase()
                        
                        # Check if user exists in Supabase
                        try:
                            # Try to sign in - if it succeeds, user exists
                            auth_response = supabase.auth.sign_in_with_password({
                                "email": admin_email,
                                "password": admin_password
                            })
                            
                            if auth_response and auth_response.user:
                                logger.info(f"Admin user {admin_email} exists in Supabase")
                                admin_id = auth_response.user.id
                                
                                # Update user metadata if needed
                                if not auth_response.user.user_metadata or auth_response.user.user_metadata.get('role') != 'admin':
                                    logger.info(f"Updating admin user metadata in Supabase")
                                    # This would require admin access to Supabase
                                    # In a real implementation, you would use Supabase admin API
                            else:
                                raise Exception("User exists but couldn't retrieve details")
                                
                        except Exception:
                            # User doesn't exist, create it
                            logger.info(f"Creating admin user {admin_email} in Supabase")
                            
                            # For now, use regular signup
                            auth_response = supabase.auth.sign_up({
                                "email": admin_email,
                                "password": admin_password,
                                "options": {
                                    "data": {
                                        "role": "admin",
                                        "name": "Admin User"
                                    }
                                }
                            })
                            
                            if auth_response and auth_response.user:
                                admin_id = auth_response.user.id
                                logger.info(f"Admin user created in Supabase with ID {admin_id}")
                            else:
                                raise Exception("Failed to create admin user in Supabase")
                    except Exception as e:
                        logger.error(f"Error managing admin user in Supabase: {str(e)}", exc_info=True)
                        # Continue with local database creation even if Supabase fails
                        admin_id = "admin-user-id"
                else:
                    # For testing, use a fixed ID
                    admin_id = "admin-user-id"
                
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
    """Sync a Supabase user to the local database."""
    # Extract user information
    user_id = supabase_user.id
    email = supabase_user.email
    metadata = supabase_user.user_metadata or {}
    role = metadata.get('role', 'plumber')
    
    # Create or update user in SQLAlchemy
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        # Create new user
        user = User(
            id=user_id,
            email=email,
            role=UserRole(role)
        )
        db.session.add(user)
    else:
        # Update existing user
        user.email = email
        user.role = UserRole(role)
    
    # Commit changes
    db.session.commit()
    return user

def signup(email, password, user_metadata=None):
    """Register a new user using Supabase Auth."""
    logger.info(f"Signup attempt for {email} with role {user_metadata.get('role') if user_metadata else 'customer'}")
    
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata  # This will be stored in user metadata
            }
        })
        
        if auth_response.user:
            logger.info(f"User {email} registered successfully with Supabase Auth")
            
            # Sync to local database
            try:
                with current_app.app_context():
                    user = sync_user_to_db(auth_response.user)
                    logger.info(f"User {email} synced to local database with ID {user.id}")
            except Exception as e:
                logger.error(f"Error syncing user {email} to local database: {str(e)}", exc_info=True)
            
            return auth_response.user
        else:
            logger.error(f"Failed to register user {email} with Supabase Auth")
            return None
            
    except Exception as e:
        logger.error(f"Error during signup for {email}: {str(e)}", exc_info=True)
        raise

def login(email, password):
    """Log in a user using Supabase Auth."""
    logger.info(f"Login attempt for {email}")
    
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Attempt login with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user and auth_response.session:
            logger.info(f"User {email} logged in successfully with Supabase Auth")
            
            # Sync user to local database
            try:
                with current_app.app_context():
                    user = sync_user_to_db(auth_response.user)
                    logger.info(f"User {email} synced to local database with ID {user.id}")
            except Exception as e:
                logger.error(f"Error syncing user {email} to local database: {str(e)}", exc_info=True)
            
            return {
                "session": auth_response.session,
                "user": auth_response.user
            }
        else:
            logger.warning(f"Login failed for {email} - invalid credentials")
            return None
            
    except Exception as e:
        logger.error(f"Error during login for {email}: {str(e)}", exc_info=True)
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
        
        # Skip authentication for login and registration routes
        if request.endpoint and (
            request.endpoint.startswith('auth.login') or 
            request.endpoint.startswith('auth.register') or
            request.endpoint.startswith('home.') or
            request.endpoint == 'static'
        ):
            logger.info(f"[{request_id}] Skipping authentication for public route: {request.path}")
            return f(*args, **kwargs)
            
        token = None
        
        # Check for token in session
        if 'token' in session:
            token = session['token']
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            logger.warning(f"[{request_id}] Token missing for protected route: {request.path}")
            
            # For API routes, return JSON response
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Authentication required'}), 401
            
            # For web routes, redirect to login
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        
        try:
            # Get Supabase client
            supabase = get_supabase()
            
            # Verify token with Supabase
            # This will throw an exception if the token is invalid or expired
            auth_response = supabase.auth.get_user(token)
            
            if not auth_response or not auth_response.user:
                raise Exception("Invalid token - user not found")
            
            # Set user info in Flask g object for access in the route
            user = auth_response.user
            user_metadata = user.user_metadata or {}
            
            g.user = {
                'id': user.id,
                'email': user.email,
                'role': user_metadata.get('role', 'customer')
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
import os
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, g, jsonify, session, flash, redirect, url_for
from app.models.plumber import Plumber
from supabase import create_client, Client

# Get the auth logger
logger = logging.getLogger('auth')

# Placeholder functions for auth service
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
            return auth_response.user
        else:
            logger.error(f"Failed to register user {email} with Supabase Auth")
            return None
            
    except Exception as e:
        logger.error(f"Error during signup for {email}: {str(e)}", exc_info=True)
        raise

def login(email, password):
    """Log in a user."""
    # In a real implementation, this would authenticate with Supabase Auth
    logger.info(f"Login attempt for {email}")
    
    # For development/testing, check for admin credentials
    if email == 'admin@example.com' and password == 'admin123':
        # Create a mock session and user object
        class MockSession:
            def __init__(self, token):
                self.access_token = token
                
        class MockUser:
            def __init__(self, id, email, metadata):
                self.id = id
                self.email = email
                self.user_metadata = metadata
                
        token = generate_token({"id": "admin-user-id", "email": email, "role": "admin"})
        session = MockSession(token)
        user = MockUser("admin-user-id", email, {"role": "admin", "name": "Admin User"})
        
        logger.info(f"Admin login successful for {email}")
        return {"session": session, "user": user}
    
    # For regular users, check credentials against database
    # This is a simplified example - in production, use proper password hashing
    try:
        # Get user role from metadata or related tables
        role = 'customer'  # Default role
        
        # Check if user is a plumber
        plumber = Plumber.get_by_user_id(email)  # In real app, use actual user_id
        if plumber:
            logger.info(f"User {email} identified as plumber with ID {plumber.id}")
            role = 'plumber'
            
            # Create session and user objects
            class MockSession:
                def __init__(self, token):
                    self.access_token = token
                    
            class MockUser:
                def __init__(self, id, email, metadata):
                    self.id = id
                    self.email = email
                    self.user_metadata = metadata
                    
            token = generate_token({"id": f"plumber-{plumber.id}", "email": email, "role": role})
            session = MockSession(token)
            
            # Set metadata based on role
            metadata = {"role": role, "company_name": plumber.company_name}
            user = MockUser(f"plumber-{plumber.id}", email, metadata)
            
            logger.info(f"Plumber login successful for {email}")
            return {"session": session, "user": user}
    except Exception as e:
        logger.error(f"Error during login for {email}: {str(e)}", exc_info=True)
    
    # Invalid credentials
    logger.warning(f"Failed login attempt for {email}")
    return None

def logout(token):
    """Log out a user by invalidating their token."""
    logger.info("Logout requested")
    
    try:
        # Decode token to get user info for logging
        payload = jwt.decode(
            token, 
            os.environ.get('SECRET_KEY', 'dev-secret-key'),
            algorithms=['HS256']
        )
        user_id = payload.get('sub')
        logger.info(f"User {user_id} logged out successfully")
    except Exception as e:
        logger.warning(f"Logout with invalid token: {str(e)}")
    
    # In a real implementation, this would invalidate the token in Supabase Auth
    return True

def reset_password_request(email):
    """Request a password reset."""
    logger.info(f"Password reset requested for {email}")
    
    # In a real implementation, this would send a reset email via Supabase Auth
    # For now, just return success
    return True

# Global variable to store Supabase client
_supabase_client = None

def init_supabase(url, key):
    """Initialize the Supabase client."""
    global _supabase_client
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
            # Decode token
            payload = jwt.decode(
                token, 
                os.environ.get('SECRET_KEY', 'dev-secret-key'),
                algorithms=['HS256']
            )
            
            # Set user info in Flask g object for access in the route
            g.user = {
                'id': payload['sub'],
                'email': payload.get('email'),
                'role': payload.get('role')
            }
            
            logger.info(f"[{request_id}] Successfully authenticated user {g.user['id']} with role {g.user.get('role')}")
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            logger.warning(f"[{request_id}] Expired token for request to {request.path}")
            
            # Clear session
            session.clear()
            
            # For API routes, return JSON response
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Token expired'}), 401
            
            # For web routes, redirect to login
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        except jwt.InvalidTokenError as e:
            logger.warning(f"[{request_id}] Invalid token for request to {request.path}: {str(e)}")
            
            # Clear session
            session.clear()
            
            # For API routes, return JSON response
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Invalid token'}), 401
            
            # For web routes, redirect to login
            flash('Authentication error. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error during authentication: {str(e)}", exc_info=True)
            return jsonify({'message': 'Authentication error'}), 500
    
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
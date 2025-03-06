import os
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, g, jsonify

# Set up a logger for use outside app context
logger = logging.getLogger(__name__)

# Placeholder functions for auth service
def signup(email, password, user_data=None):
    """Register a new user."""
    # In a real implementation, this would create a user in Supabase Auth
    logger.info(f"Signup attempt for {email}")
    return {"user_id": "mock-user-id", "email": email}

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
        
        return {"session": session, "user": user}
    
    # For plumber accounts
    if email.startswith('plumber') and password == 'password123':
        plumber_id = email.split('@')[0].replace('plumber', '')
        try:
            plumber_id = int(plumber_id)
            # Create a mock session and user object
            class MockSession:
                def __init__(self, token):
                    self.access_token = token
                    
            class MockUser:
                def __init__(self, id, email, metadata):
                    self.id = id
                    self.email = email
                    self.user_metadata = metadata
                    
            token = generate_token({"id": f"plumber-{plumber_id}", "email": email, "role": "plumber"})
            session = MockSession(token)
            user = MockUser(f"plumber-{plumber_id}", email, {"role": "plumber", "company_name": f"Plumber Company {plumber_id}"})
            
            return {"session": session, "user": user}
        except ValueError:
            pass
    
    # Invalid credentials
    return None

def logout(token):
    """Log out a user."""
    # In a real implementation, this would invalidate the token
    logger.info("Logout attempt")
    return {"success": True}

def reset_password_request(email):
    """Request a password reset."""
    # In a real implementation, this would trigger a password reset email
    logger.info(f"Password reset requested for {email}")
    return {"success": True}

# Global variable to store Supabase client
_supabase_client = None

def init_supabase(url, key):
    """Initialize the Supabase client."""
    global _supabase_client
    # In a real implementation, this would initialize the Supabase client
    logger.info(f"Initializing Supabase with URL: {url}")
    _supabase_client = {"url": url, "key": key}
    return _supabase_client

def get_supabase_client():
    """Get the Supabase client."""
    global _supabase_client
    if not _supabase_client:
        # If not initialized, return a mock client
        return {"url": "mock-url", "key": "mock-key"}
    return _supabase_client

def generate_token(user_data):
    """Generate a JWT token for a user."""
    secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_data.get('id'),
        'email': user_data.get('email'),
        'role': user_data.get('role', 'plumber')
    }
    return jwt.encode(
        payload,
        secret_key,
        algorithm='HS256'
    )

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
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # If no token, return 401
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Set user in g
        g.user = {
            'id': payload.get('sub'),
            'email': payload.get('email'),
            'role': payload.get('role')
        }
        
        return f(*args, **kwargs)
    
    return decorated

def plumber_required(f):
    """Decorator to require a plumber role for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if user is set in g
        if not hasattr(g, 'user'):
            return jsonify({'message': 'Authentication required'}), 401
        
        # Check if user has plumber role
        if g.user.get('role') != 'plumber':
            return jsonify({'message': 'Plumber role required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require an admin role for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if user is set in g
        if not hasattr(g, 'user'):
            return jsonify({'message': 'Authentication required'}), 401
        
        # Check if user has admin role
        if g.user.get('role') != 'admin':
            return jsonify({'message': 'Admin role required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated 
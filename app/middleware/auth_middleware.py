from functools import wraps
from flask import request, redirect, url_for, session, g
from app.services.auth_service import get_current_user
import logging

# Get the auth logger
logger = logging.getLogger('auth')

def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            logger.warning("Unauthorized access attempt - no user_id in session")
            return redirect(url_for('auth.login'))
        
        # Get current user
        user = get_current_user()
        if not user:
            logger.warning("Unauthorized access attempt - invalid user")
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Store user in g for easy access
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            logger.warning("Admin access attempt - no user_id in session")
            return redirect(url_for('auth.login'))
        
        # Get current user
        user = get_current_user()
        if not user or user.user_metadata.get('role') != 'admin':
            logger.warning(f"Admin access attempt by user {session.get('user_id')}")
            return redirect(url_for('home.index'))
        
        # Store user in g for easy access
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

def plumber_required(f):
    """Decorator to require plumber role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            logger.warning("Plumber access attempt - no user_id in session")
            return redirect(url_for('auth.login'))
        
        # Get current user
        user = get_current_user()
        if not user or user.user_metadata.get('role') != 'plumber':
            logger.warning(f"Plumber access attempt by user {session.get('user_id')}")
            return redirect(url_for('home.index'))
        
        # Store user in g for easy access
        g.user = user
        return f(*args, **kwargs)
    return decorated_function 
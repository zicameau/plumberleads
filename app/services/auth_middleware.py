from functools import wraps
from flask import request, redirect, url_for, session, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in session first
        if 'token' in session:
            token = session['token']
        # Then check Authorization header
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login', next=request.url))
            
        # Store token in request context
        request.token = token
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            user_role = session.get('user', {}).get('role')
            if not user_role or user_role != role:
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({'error': 'Insufficient permissions'}), 403
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

admin_required = role_required('admin')
plumber_required = role_required('plumber') 
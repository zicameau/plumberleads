from functools import wraps
from flask import request
from .errors import AuthenticationError
from ..services.auth_service import AuthService

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            raise AuthenticationError("No authorization header")

        try:
            # Extract token from Bearer token
            token = auth_header.split(' ')[1]
            user = AuthService.verify_token(token)
            
            if not user:
                raise AuthenticationError("Invalid token")

            # Add user to request context
            request.user = user
            return f(*args, **kwargs)
            
        except IndexError:
            raise AuthenticationError("Invalid authorization header format")
        except Exception as e:
            raise AuthenticationError(str(e))
            
    return decorated 
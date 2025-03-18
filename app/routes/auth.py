from flask import Blueprint, request, jsonify
from ..services.auth_service import AuthService
from ..utils.errors import ValidationError, AuthenticationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new plumber"""
    data = request.get_json()
    
    if not data:
        raise ValidationError("No data provided")
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'phone_number']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"Missing required field: {field}")
    
    result = AuthService.register_plumber(data)
    return jsonify(result), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a plumber"""
    data = request.get_json()
    
    if not data:
        raise ValidationError("No data provided")
    
    if not data.get('email') or not data.get('password'):
        raise ValidationError("Email and password are required")
    
    result = AuthService.login(data['email'], data['password'])
    return jsonify(result)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a plumber"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise AuthenticationError("No authorization header")
    
    try:
        # Extract token from Bearer token
        token = auth_header.split(' ')[1]
        AuthService.logout(token)
        return jsonify({"message": "Successfully logged out"})
    except IndexError:
        raise AuthenticationError("Invalid authorization header format")
    except Exception as e:
        raise AuthenticationError(str(e)) 
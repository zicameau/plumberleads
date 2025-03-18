from flask import Blueprint, request, jsonify
from ..services.auth_service import AuthService
from ..utils.errors import ValidationError, AuthenticationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new plumber"""
    if not request.is_json or not request.get_data():
        return jsonify({"error": {"message": "No data provided"}}), 400
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": {"message": "No data provided"}}), 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'phone_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": {"message": f"Missing required field: {field}"}}), 400
        
        result = AuthService.register_plumber(data)
        return jsonify(result["user"]), 201
    except AuthenticationError as e:
        # Explicitly handle the authentication error
        error_message = str(e) or "Failed to create user"
        return jsonify({"error": {"message": error_message}}), 401
    except ValidationError as e:
        return jsonify({"error": {"message": str(e)}}), 400
    except Exception as e:
        return jsonify({"error": {"message": "Invalid request format"}}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a plumber"""
    if not request.is_json or not request.get_data():
        return jsonify({"error": {"message": "No data provided"}}), 400
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": {"message": "No data provided"}}), 400
        
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": {"message": "Email and password are required"}}), 400
        
        result = AuthService.login(data['email'], data['password'])
        return jsonify(result)
    except AuthenticationError as e:
        # Explicitly handle the authentication error
        error_message = str(e) or "Invalid credentials"
        return jsonify({"error": {"message": error_message}}), 401
    except ValidationError as e:
        return jsonify({"error": {"message": str(e)}}), 400
    except Exception as e:
        return jsonify({"error": {"message": "Invalid request format"}}), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a plumber"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({"error": {"message": "No authorization header"}}), 401
    
    try:
        # Extract token from Bearer token
        token = auth_header.split(' ')[1]
        AuthService.logout(token)
        return jsonify({"message": "Successfully logged out"})
    except IndexError:
        return jsonify({"error": {"message": "Invalid authorization header format"}}), 401
    except AuthenticationError as e:
        # Explicitly handle the authentication error
        error_message = str(e) or "Auth service error"
        return jsonify({"error": {"message": error_message}}), 401
    except Exception as e:
        return jsonify({"error": {"message": str(e) if hasattr(e, 'args') and e.args else "Auth service error"}}), 401 
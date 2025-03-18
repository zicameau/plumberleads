from flask import jsonify
from ..utils.auth_middleware import require_auth
from . import api_bp

@api_bp.route('/protected')
@require_auth
def protected_route():
    """A protected route that requires authentication"""
    return jsonify({"message": "Access granted", "user": "test_user"}) 
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
from .utils.errors import APIError, ValidationError, handle_api_error
from .utils.supabase import init_database
from .routes.auth import auth_bp
from .api import api_bp

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Register error handlers
    app.register_error_handler(APIError, handle_api_error)
    
    # Handle JSON parsing errors
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        if "Failed to decode JSON" in str(e):
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request format"
                }
            }), 400
        return jsonify({
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "No data provided"
            }
        }), 400

    # Handle general exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, APIError):
            return handle_api_error(e)
        return jsonify({
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500

    # Initialize database
    with app.app_context():
        init_database()

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})

    return app 
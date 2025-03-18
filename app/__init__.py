from flask import Flask
from flask_cors import CORS
from .utils.errors import APIError, handle_api_error
from .utils.supabase import init_database

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Register error handlers
    app.register_error_handler(APIError, handle_api_error)
    
    # Initialize database
    with app.app_context():
        init_database()
    
    # Register blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app 
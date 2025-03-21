import os
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from flask_session import Session
from config import Config

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
sess = Session()

# Import models to ensure they are registered with SQLAlchemy
from app.models import user, lead, payment
from app.models.user import User

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    sess.init_app(app)
    
    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Set security headers
    @app.after_request
    def add_security_headers(response):
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
        return response
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.leads import bp as leads_bp
    app.register_blueprint(leads_bp, url_prefix='/leads')
    
    from app.plumber import bp as plumber_bp
    app.register_blueprint(plumber_bp, url_prefix='/plumber')
    
    # Create upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create database tables if in local development mode
    if app.config['LOCAL_DEV']:
        with app.app_context():
            db.create_all()
    
    # Simple index route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'environment': app.config['FLASK_ENV'],
            'version': os.environ.get('APP_VERSION', '1.0.0')
        })
    
    # Handle 404 errors
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    # Handle 500 errors
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    return app 
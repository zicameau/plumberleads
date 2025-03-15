# app/__init__.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mail import Mail
from app.utils.logging_config import setup_logging

# Initialize SQLAlchemy
from app.models.base import db

# Initialize mail
mail = Mail()

def create_app(config_name=None):
    """Create and configure the Flask application."""
    print(f"\nCreating app from: {__file__}")
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')

    # Load appropriate configuration
    if config_name == 'production':
        from app.config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'development':
        from app.config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'testing':
        from app.config.testing import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from app.config.local import LocalConfig
        app.config.from_object(LocalConfig)

    # Initialize SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Set up logging
    loggers = setup_logging(app)
    app.loggers = loggers
    
    # Register blueprints
    from app.routes.home import home_bp
    app.register_blueprint(home_bp)
    
    try:
        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError as e:
        print(f"Warning: Could not import auth blueprint: {e}")
    
    try:
        from app.routes.customer import customer_bp
        app.register_blueprint(customer_bp)
    except ImportError as e:
        print(f"Warning: Could not import customer blueprint: {e}")
    
    try:
        from app.routes.plumber import plumber_bp
        app.register_blueprint(plumber_bp)
    except ImportError as e:
        print(f"Warning: Could not import plumber blueprint: {e}")
    
    try:
        from app.routes.admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError as e:
        print(f"Warning: Could not import admin blueprint: {e}")
    
    # Initialize Supabase with configuration 
    from app.services.auth_service import init_supabase, init_admin_user
    init_supabase(
        app.config['SUPABASE_URL'],
        app.config['SUPABASE_KEY'],
        testing=app.config.get('TESTING', False)
    )
    
    # Initialize admin user
    with app.app_context():
        init_admin_user()
    
    # Initialize Stripe
    from app.services.payment_service import init_stripe
    init_stripe(app.config['STRIPE_API_KEY'])
    
    # Initialize mail
    mail.init_app(app)
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app
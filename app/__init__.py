# app/__init__.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mail import Mail

# Try to import SQLAlchemy, but don't fail if it's not available
try:
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    db = SQLAlchemy()
    migrate = Migrate()
    has_sqlalchemy = True
except ImportError:
    has_sqlalchemy = False
    db = None
    migrate = None
    print("Warning: SQLAlchemy not available. Running in limited mode.")

# Load environment variables
load_dotenv()

# Initialize mail
mail = Mail()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Initialize extensions if available
    if has_sqlalchemy:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        migrate.init_app(app, db)
    
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
    
    # Create Supabase client
    from app.services.auth_service import init_supabase
    init_supabase(
        app.config['SUPABASE_URL'],
        app.config['SUPABASE_KEY']
    )
    
    # Initialize Stripe
    from app.services.payment_service import init_stripe
    init_stripe(app.config['STRIPE_API_KEY'])
    
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}
    
    return app

# app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mail import Mail

# Load environment variables
load_dotenv()

# Initialize mail
mail = Mail()

def create_app(config_name=None):
    app = Flask(__name__)
    CORS(app)  # Enable CORS
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')
    
    # Initialize extensions
    mail.init_app(app)  # Initialize Flask-Mail
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.customer import customer_bp
    from app.routes.plumber import plumber_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(plumber_bp)
    app.register_blueprint(admin_bp)
    
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

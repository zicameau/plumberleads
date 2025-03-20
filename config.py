"""
Application configuration settings.
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///plumberleads.db'
    
    # Fix SQLite URI for SQLAlchemy 1.4+
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
        # SQLite connection is already correct
        pass
    elif SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        # To work with SQLAlchemy 1.4+, update postgres:// to postgresql://
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://')
    
    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Stripe settings
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Supabase settings
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Local development mode
    LOCAL_DEV = os.environ.get('LOCAL_DEV', 'False').lower() in ['true', '1', 't']
    
    # Default lead pricing (in USD)
    DEFAULT_LEAD_PRICE = 15.00
    
    # Service areas and types
    SERVICE_AREAS = [
        'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
        'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'
    ]
    
    SERVICE_TYPES = [
        'Emergency Repair', 'Leak Detection', 'Drain Cleaning',
        'Pipe Installation', 'Water Heater Service', 'Fixture Installation',
        'Sewer Repair', 'Backflow Testing', 'Water Line Repair', 'Commercial Plumbing'
    ]

    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Set SQLite as a fallback if DATABASE_URL is not set
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///plumberleads.db'
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 
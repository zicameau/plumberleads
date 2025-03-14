import os
from dotenv import load_dotenv

load_dotenv('.env.test')

class TestingConfig:
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SERVER_NAME = None  # Changed from 'localhost.localdomain' to avoid binding issues
    
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    
    # Mail settings for testing
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 25))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', '1', 't')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False
    
    # Supabase mock settings
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Stripe mock settings
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    # Subscription settings
    MONTHLY_SUBSCRIPTION_PRICE_ID = os.getenv('MONTHLY_SUBSCRIPTION_PRICE_ID')
    
    # Business settings
    APP_NAME = os.getenv('APP_NAME', 'Plumber Leads (Testing)')
    LEAD_RADIUS_MILES = int(os.getenv('LEAD_RADIUS_MILES', 25))
    LEAD_PRICE = float(os.getenv('LEAD_PRICE', 10.00))
    
    # Twilio mock settings
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    # HTTPS settings
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True 
    
    # Add other test configuration as needed 
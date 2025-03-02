import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DevelopmentConfig:
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Stripe (use test keys for development)
    STRIPE_API_KEY = os.getenv('STRIPE_TEST_API_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_TEST_WEBHOOK_SECRET')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_TEST_PUBLISHABLE_KEY')
    
    # Subscription settings (test price IDs)
    MONTHLY_SUBSCRIPTION_PRICE_ID = os.getenv('MONTHLY_SUBSCRIPTION_PRICE_ID_TEST')
    
    # Email settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'mailhog')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 1025))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # SMS settings (Twilio test credentials)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_TEST_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_TEST_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_TEST_PHONE_NUMBER')
    
    # Business Settings
    APP_NAME = os.getenv('APP_NAME', 'Plumber Leads (Development)')
    LEAD_RADIUS_MILES = int(os.getenv('LEAD_RADIUS_MILES', 25))
    LEAD_PRICE = float(os.getenv('LEAD_PRICE', 10.00)) 
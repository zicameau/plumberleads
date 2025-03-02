import os

class TestingConfig:
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-key'
    SERVER_NAME = 'localhost.localdomain'
    
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings for testing
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'testing@example.com'
    
    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False 
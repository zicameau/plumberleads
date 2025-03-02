def create_app(config_name=None):
    """Create and configure the Flask application."""
    from flask import Flask
    import os
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Determine configuration to use
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    # Load appropriate configuration
    if config_name == 'production':
        from app.config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'development':
        from app.config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    else:
        from app.config.local import LocalConfig
        app.config.from_object(LocalConfig)
    
    # Register blueprints, initialize extensions, etc.
    # ... rest of your initialization code ...
    
    return app 
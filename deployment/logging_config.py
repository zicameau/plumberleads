import os
import logging
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    """Configure logging for the application."""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format
    )
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('/app/logs'):
        os.makedirs('/app/logs')
    
    # Create file handler for app.log
    file_handler = RotatingFileHandler(
        '/app/logs/app.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(getattr(logging, log_level))
    
    # Add file handler to app logger
    app.logger.addHandler(file_handler)
    
    # Set app logger level
    app.logger.setLevel(getattr(logging, log_level))
    
    # Log startup information
    app.logger.info(f"Starting application in {app.config.get('ENV', 'production')} mode")
    app.logger.info(f"Log level set to {log_level}")
    
    # Log all registered routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ', '.join(rule.methods),
            'path': str(rule)
        })
    
    app.logger.info(f"Registered routes: {len(routes)}")
    for route in routes:
        app.logger.debug(f"Route: {route['endpoint']} - {route['methods']} - {route['path']}")
    
    return app.logger 
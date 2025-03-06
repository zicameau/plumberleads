import os
import logging
from logging.handlers import RotatingFileHandler
import time

def setup_logging(app):
    """Configure application logging with detailed formatting and file rotation."""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(app.root_path, '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up file paths
    general_log = os.path.join(log_dir, 'app.log')
    error_log = os.path.join(log_dir, 'error.log')
    auth_log = os.path.join(log_dir, 'auth.log')
    
    # Configure logging format
    log_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    # General application logger
    general_handler = RotatingFileHandler(
        general_log, maxBytes=10485760, backupCount=10
    )
    general_handler.setFormatter(log_format)
    general_handler.setLevel(logging.INFO)
    
    # Error logger (separate file for errors)
    error_handler = RotatingFileHandler(
        error_log, maxBytes=10485760, backupCount=10
    )
    error_handler.setFormatter(log_format)
    error_handler.setLevel(logging.ERROR)
    
    # Authentication logger (separate file for auth events)
    auth_handler = RotatingFileHandler(
        auth_log, maxBytes=10485760, backupCount=10
    )
    auth_handler.setFormatter(log_format)
    auth_handler.setLevel(logging.INFO)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Configure Flask app logger
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.addHandler(general_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    
    # Create and configure auth logger
    auth_logger = logging.getLogger('auth')
    auth_logger.setLevel(logging.INFO)
    auth_logger.addHandler(auth_handler)
    auth_logger.addHandler(console_handler)
    
    # Create and configure database logger
    db_logger = logging.getLogger('database')
    db_logger.setLevel(logging.INFO)
    db_logger.addHandler(general_handler)
    db_logger.addHandler(console_handler)
    
    # Create and configure payment logger
    payment_logger = logging.getLogger('payment')
    payment_logger.setLevel(logging.INFO)
    payment_logger.addHandler(general_handler)
    payment_logger.addHandler(console_handler)
    
    # Log application startup
    app.logger.info(f"Application started in {app.config['ENV']} mode")
    
    return {
        'app': app.logger,
        'auth': auth_logger,
        'db': db_logger,
        'payment': payment_logger
    } 
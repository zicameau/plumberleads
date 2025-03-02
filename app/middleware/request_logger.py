import time
import logging
from flask import request, g

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Log request
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        remote_addr = environ.get('REMOTE_ADDR', '')
        
        logger.info(f"Request: {method} {path} from {remote_addr}")
        
        # Set start time
        g.start_time = time.time()
        
        # Define a custom response handler
        def custom_start_response(status, headers, exc_info=None):
            # Log response
            status_code = status.split(' ')[0]
            duration = time.time() - g.start_time
            logger.info(f"Response: {status_code} for {method} {path} in {duration:.4f}s")
            
            # Call the original start_response
            return start_response(status, headers, exc_info)
        
        # Process the request
        return self.app(environ, custom_start_response)

def init_request_logger(app):
    """Initialize request logger middleware."""
    app.wsgi_app = RequestLoggerMiddleware(app.wsgi_app)
    return app 
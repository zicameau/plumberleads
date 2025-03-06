from flask import render_template, jsonify, request, current_app
import logging
import traceback

# Get the app logger
logger = logging.getLogger('app')

def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        logger.warning(f"404 Not Found: {request.path}")
        
        # Return JSON for API requests
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'The requested resource was not found on this server.'
            }), 404
        
        # Return HTML for web requests
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        # Get exception details
        exc_info = traceback.format_exc()
        logger.error(f"500 Internal Server Error: {str(error)}\n{exc_info}")
        
        # Return JSON for API requests
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': 'The server encountered an internal error and was unable to complete your request.'
            }), 500
        
        # Return HTML for web requests
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors."""
        logger.warning(f"403 Forbidden: {request.path}")
        
        # Return JSON for API requests
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': False,
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource.'
            }), 403
        
        # Return HTML for web requests
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 errors."""
        logger.warning(f"401 Unauthorized: {request.path}")
        
        # Return JSON for API requests
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Authentication is required to access this resource.'
            }), 401
        
        # Return HTML for web requests
        return render_template('errors/401.html'), 401 
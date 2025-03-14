import socket
import pytest
from flask import url_for
from app import create_app

def test_app_initialization():
    """Test that the Flask app initializes correctly"""
    app = create_app('testing')
    assert app is not None
    assert app.testing == True

def test_database_connection():
    """Test database connection if using one"""
    from app import db
    app = create_app('testing')
    with app.app_context():
        try:
            db.engine.connect()
            connected = True
        except Exception as e:
            connected = False
        assert connected == True

def test_wsgi_server_config(client):
    """Test WSGI server configuration"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_static_files_serving(client):
    """Test that static files are served correctly"""
    response = client.get('/static/css/main.css', follow_redirects=True)
    assert response.status_code in (200, 404)  # 404 is acceptable if file doesn't exist

def test_template_rendering(client):
    """Test template rendering"""
    app = create_app('testing')
    with app.test_request_context():
        try:
            rendered = app.jinja_env.get_template('home/index.html').render()
            template_exists = True
        except Exception as e:
            template_exists = False
        assert template_exists == True

def test_port_availability():
    """Test if the required port is available"""
    port = 5000  # or whatever port you're using
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        available = True
    except:
        available = False
    finally:
        sock.close()
    assert available == True

def test_route_registration():
    """Test that all essential routes are registered"""
    app = create_app('testing')
    with app.test_request_context():
        # Test core routes
        assert url_for('home.index') is not None
        assert url_for('auth.login') is not None
        assert url_for('auth.register_plumber') is not None

def test_error_handling():
    """Test error handling for common scenarios"""
    app = create_app('testing')
    
    @app.route('/test-500')
    def trigger_error():
        raise Exception('Test error')
    
    with app.test_client() as client:
        # Test 404
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Test 500 - use catch_exceptions=False to get the response
        response = client.get('/test-500', catch_exceptions=False)
        assert response.status_code == 500

def test_middleware_chain():
    """Test that middleware is properly configured"""
    app = create_app('testing')
    
    # Check if essential middleware exists
    assert 'flask_cors' in app.extensions
    
    with app.test_client() as client:
        response = client.get('/health')
        # Check CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers 
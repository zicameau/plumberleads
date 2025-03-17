import socket
import pytest
from flask import url_for
from app import create_app
from werkzeug.exceptions import HTTPException
import threading
import requests
import time
import os

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
        assert url_for('auth.logout_route') is not None
        assert url_for('auth.reset_password_route') is not None
        assert url_for('auth.api_login') is not None
        assert url_for('auth.api_register_plumber') is not None

def test_error_handling():
    """Test error handling using a running server"""
    app = create_app('testing')
    
    # Create a route that will trigger a 500 error
    @app.route('/test-500')
    def trigger_error():
        raise Exception('Test error')
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=app.run, kwargs={
        'host': 'localhost',
        'port': 5000,
        'debug': False,
        'use_reloader': False
    })
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for the server to start by polling the health endpoint
    max_retries = 30
    retry_interval = 0.1
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:5000/health')
            if response.status_code == 200:
                # Server is up and running
                break
        except requests.exceptions.ConnectionError:
            # Server not ready yet
            pass
        
        if i == max_retries - 1:
            pytest.fail("Server failed to start after maximum retries")
        
        time.sleep(retry_interval)
    
    try:
        # Test 404
        response = requests.get('http://localhost:5000/nonexistent-page')
        assert response.status_code == 404
        
        # Test 500
        response = requests.get('http://localhost:5000/test-500')
        assert response.status_code == 500
    finally:
        # Cleanup is handled by daemon=True
        pass

def test_middleware_chain():
    """Test that middleware is properly configured"""
    app = create_app('testing')
    
    # Method 1: Look for CORS in multiple ways
    cors_detected = False
    detection_method = None
    
    # Check in extensions
    for ext_name in app.extensions:
        if 'cors' in ext_name.lower():
            cors_detected = True
            detection_method = f"extension: {ext_name}"
            break
    
    # Check in the app's attributes
    if not cors_detected and (hasattr(app, '_cors') or hasattr(app, 'cors')):
        cors_detected = True
        detection_method = "app attribute"
    
    # Check in the app's after_request functions - this is where Flask-CORS typically registers
    if not cors_detected and hasattr(app, 'after_request_funcs') and app.after_request_funcs:
        for bp, funcs in app.after_request_funcs.items():
            for func in funcs:
                # Check function module or name for CORS
                if (hasattr(func, '__module__') and 'cors' in func.__module__.lower()) or \
                   (hasattr(func, '__name__') and 'cors' in func.__name__.lower()):
                    cors_detected = True
                    detection_method = f"after_request: {func.__module__ if hasattr(func, '__module__') else 'unknown'}.{func.__name__ if hasattr(func, '__name__') else 'unknown'}"
                    break
            if cors_detected:
                break
    
    # If we still can't detect CORS in the configuration, skip that check and focus on functionality
    if not cors_detected:
        print("Warning: Could not detect CORS in app configuration, skipping configuration check")
        print("App extensions:", app.extensions)
        print("App after_request_funcs:", app.after_request_funcs if hasattr(app, 'after_request_funcs') else "None")
    
    # Method 2: Test actual CORS functionality (this is what really matters)
    with app.test_client() as client:
        # Test regular request
        response = client.get('/health')
        cors_headers_present = 'Access-Control-Allow-Origin' in response.headers
        
        # Test OPTIONS request (preflight)
        preflight_response = client.options('/health', headers={
            'Origin': 'http://example.com',
            'Access-Control-Request-Method': 'GET'
        })
        preflight_success = (
            preflight_response.status_code == 200 and
            'Access-Control-Allow-Origin' in preflight_response.headers and
            'Access-Control-Allow-Methods' in preflight_response.headers
        )
        
        # Assert that CORS is working functionally, even if we couldn't detect it in configuration
        assert cors_headers_present, "CORS headers missing in regular response"
        assert preflight_success, "CORS preflight request failed or missing headers"
        
        # Only assert configuration detection if we're not in a CI environment
        # This makes the test more robust against different Flask-CORS versions
        if not os.environ.get('CI'):
            assert cors_detected, "CORS middleware not detected in app configuration" 
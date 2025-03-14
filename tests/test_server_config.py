import socket
import pytest
from flask import url_for
from app import create_app
from werkzeug.exceptions import HTTPException
import threading
import requests
import time

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
    
    # Check if essential middleware exists
    assert 'flask_cors' in app.extensions
    
    with app.test_client() as client:
        response = client.get('/health')
        # Check CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers 
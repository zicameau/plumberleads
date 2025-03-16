import pytest
import os
import sys
from flask import g, session, request, url_for
from app.services.auth_service import token_required, admin_required, plumber_required, login

# Add the parent directory to sys.path to allow importing from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_token_required_decorator(app, client, monkeypatch):
    """Test the token_required decorator."""
    # Set environment variables for testing
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin123')
    
    with app.app_context():
        # Create a test route with the token_required decorator
        @app.route('/test/protected')
        @token_required
        def protected_route():
            return {'success': True, 'user_id': g.user['id'], 'role': g.user['role']}
        
        # Mock the token verification to set up g.user
        def mock_verify_token(token):
            if token == 'mock-token-admin':
                g.user = {
                    'id': 'test-admin-id',
                    'role': 'admin'
                }
                return True
            return False
        
        # Patch the verify_token function
        monkeypatch.setattr('app.services.auth_service.verify_token', mock_verify_token)
        
        # Test accessing the protected route with a valid token in the header
        response = client.get('/test/protected', headers={
            'Authorization': f'Bearer mock-token-admin'
        })
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['role'] == 'admin'
        
        # Test accessing the protected route with a valid token in the session
        with client.session_transaction() as sess:
            sess['token'] = 'mock-token-admin'
        
        response = client.get('/test/protected')
        assert response.status_code == 200
        assert response.json['success'] is True
        
        # Test accessing the protected route without a token
        client.cookie_jar.clear()
        response = client.get('/test/protected', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data

def test_admin_required_decorator(app, client, monkeypatch):
    """Test the admin_required decorator."""
    # Set environment variables for testing
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin123')
    
    with app.app_context():
        # Create a test route with the admin_required decorator
        @app.route('/test/admin')
        @token_required
        @admin_required
        def admin_route():
            return {'success': True, 'role': g.user['role']}
        
        # Create a test route with the token_required decorator for a plumber
        @app.route('/test/plumber')
        @token_required
        @plumber_required
        def plumber_route():
            return {'success': True, 'role': g.user['role']}
        
        # Mock the token verification to set up g.user
        def mock_verify_token(token):
            if token == 'mock-token-admin':
                g.user = {
                    'id': 'test-admin-id',
                    'role': 'admin'
                }
                return True
            elif token == 'mock-token-plumber':
                g.user = {
                    'id': 'test-plumber-id',
                    'role': 'plumber'
                }
                return True
            return False
        
        # Patch the verify_token function
        monkeypatch.setattr('app.services.auth_service.verify_token', mock_verify_token)
        
        # Test accessing the admin route with an admin token
        response = client.get('/test/admin', headers={
            'Authorization': f'Bearer mock-token-admin'
        })
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['role'] == 'admin'
        
        # Test accessing the plumber route with an admin token (should fail)
        response = client.get('/test/plumber', headers={
            'Authorization': f'Bearer mock-token-admin'
        })
        
        assert response.status_code == 403
        assert response.json['message'] == 'Plumber role required'
        
        # Test accessing the plumber route with a plumber token
        response = client.get('/test/plumber', headers={
            'Authorization': f'Bearer mock-token-plumber'
        })
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['role'] == 'plumber'
        
        # Test accessing the admin route with a plumber token (should fail)
        response = client.get('/test/admin', headers={
            'Authorization': f'Bearer mock-token-plumber'
        })
        
        assert response.status_code == 403
        assert response.json['message'] == 'Admin role required'

def test_public_routes_bypass_auth(app, client):
    """Test that public routes bypass authentication."""
    with app.app_context():
        # Create a test route with the token_required decorator
        @app.route('/test/public')
        def public_route():
            return {'success': True}
        
        # Test accessing the public route without a token
        response = client.get('/test/public')
        assert response.status_code == 200
        assert response.json['success'] is True
        
        # Test accessing the login page without a token
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        # Test accessing the registration page without a token
        response = client.get('/auth/register/plumber')
        assert response.status_code == 200
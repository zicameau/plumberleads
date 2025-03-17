import pytest
import os
import sys
from flask import Blueprint, g, session, request, url_for
from app.services.auth_service import token_required, admin_required, plumber_required, login

# Add the parent directory to sys.path to allow importing from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def test_bp(app):
    """Create a test blueprint for auth middleware tests."""
    bp = Blueprint('test', __name__)
    
    @bp.route('/test/protected')
    @token_required
    def protected_route():
        return {'success': True, 'user_id': g.user['id'], 'role': g.user['role']}
    
    @bp.route('/test/admin')
    @token_required
    @admin_required
    def admin_route():
        return {'success': True, 'role': g.user['role']}
    
    @bp.route('/test/plumber')
    @token_required
    @plumber_required
    def plumber_route():
        return {'success': True, 'role': g.user['role']}
    
    @bp.route('/test/public')
    def public_route():
        return {'success': True}
    
    # Register blueprint before any requests are made
    app.register_blueprint(bp)
    return bp

def test_token_required_decorator(app, client, monkeypatch, test_bp):
    """Test the token_required decorator."""
    # Set environment variables for testing
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin123')
    
    # Create a mock Supabase client
    class MockSupabaseClient:
        class Auth:
            def get_user(self, token):
                if token == 'mock-token-admin':
                    from collections import namedtuple
                    User = namedtuple('User', ['id', 'email', 'user_metadata'])
                    return namedtuple('AuthResponse', ['user'])(user=User(
                        id='test-admin-id',
                        email='admin@example.com',
                        user_metadata={'role': 'admin'}
                    ))
                return None
        
        def __init__(self):
            self.auth = self.Auth()
    
    # Mock the get_supabase function to return our mock client
    monkeypatch.setattr('app.services.auth_service.get_supabase', lambda: MockSupabaseClient())
    
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

def test_admin_required_decorator(app, client, monkeypatch, test_bp):
    """Test the admin_required decorator."""
    # Set environment variables for testing
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin123')
    
    # Create a mock Supabase client
    class MockSupabaseClient:
        class Auth:
            def get_user(self, token):
                from collections import namedtuple
                User = namedtuple('User', ['id', 'email', 'user_metadata'])
                if token == 'mock-token-admin':
                    return namedtuple('AuthResponse', ['user'])(user=User(
                        id='test-admin-id',
                        email='admin@example.com',
                        user_metadata={'role': 'admin'}
                    ))
                elif token == 'mock-token-plumber':
                    return namedtuple('AuthResponse', ['user'])(user=User(
                        id='test-plumber-id',
                        email='plumber@example.com',
                        user_metadata={'role': 'plumber'}
                    ))
                return None
        
        def __init__(self):
            self.auth = self.Auth()
    
    # Mock the get_supabase function to return our mock client
    monkeypatch.setattr('app.services.auth_service.get_supabase', lambda: MockSupabaseClient())
    
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

def test_public_routes_bypass_auth(app, client, test_bp):
    """Test that public routes bypass authentication."""
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
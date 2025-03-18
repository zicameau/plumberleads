import pytest
import os
import sys
from flask import g, session, request, url_for
from app.services.auth_service import token_required, admin_required, plumber_required, login
from app.services.supabase import get_supabase

# Add the parent directory to sys.path to allow importing from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_token_required_decorator(app, client, test_user):
    """Test the token_required decorator."""
    # First login to get a token
    response = client.post('/auth/login', data={
        'email': test_user['email'],
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in session
    
    # Test accessing a protected route with valid token
    response = client.get('/api/profile', headers={
        'Authorization': f'Bearer {session["token"]}'
    })
    assert response.status_code == 200
    
    # Test accessing a protected route without token
    response = client.get('/api/profile')
    assert response.status_code == 401
    
    # Test accessing a protected route with invalid token
    response = client.get('/api/profile', headers={
        'Authorization': 'Bearer invalid_token'
    })
    assert response.status_code == 401

def test_role_required_decorator(app, client, test_plumber):
    """Test the role_required decorator."""
    # Login as plumber
    response = client.post('/auth/login', data={
        'email': test_plumber['user']['email'],
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in session
    
    # Test accessing plumber route with plumber role
    response = client.get('/api/plumber/profile', headers={
        'Authorization': f'Bearer {session["token"]}'
    })
    assert response.status_code == 200
    
    # Test accessing admin route with plumber role (should fail)
    response = client.get('/api/admin/dashboard', headers={
        'Authorization': f'Bearer {session["token"]}'
    })
    assert response.status_code == 403

def test_public_routes_access(app, client):
    """Test that public routes are accessible without authentication."""
    public_routes = [
        '/',
        '/auth/login',
        '/auth/register/plumber',
        '/auth/reset-password',
        '/health'
    ]
    
    for route in public_routes:
        response = client.get(route)
        assert response.status_code == 200

def test_protected_routes_redirect(app, client):
    """Test that protected routes redirect to login when not authenticated."""
    protected_routes = [
        '/api/profile',
        '/api/plumber/profile',
        '/api/admin/dashboard'
    ]
    
    for route in protected_routes:
        response = client.get(route, follow_redirects=True)
        assert b'Please log in' in response.data

def test_api_routes_unauthorized(app, client):
    """Test that API routes return 401 when not authenticated."""
    api_routes = [
        '/api/profile',
        '/api/plumber/profile',
        '/api/admin/dashboard'
    ]
    
    for route in api_routes:
        response = client.get(route, headers={'Accept': 'application/json'})
        assert response.status_code == 401
        assert 'error' in response.json
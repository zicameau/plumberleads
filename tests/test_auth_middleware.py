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

def test_public_routes(app, client):
    """Test public routes are accessible without authentication."""
    # Test home page
    response = client.get('/')
    assert response.status_code == 200
    
    # Test login page
    response = client.get('/auth/login')
    assert response.status_code == 200
    
    # Test registration page
    response = client.get('/auth/register/plumber')
    assert response.status_code == 200
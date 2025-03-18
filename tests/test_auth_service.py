import pytest
import os
from flask import session
from app.services.auth_service import init_admin_user, login, signup, logout, reset_password_request

def test_signup_and_login(app, client):
    """Test user signup and login functionality."""
    with app.test_request_context():
        # Test signup
        response = client.post('/auth/register/customer', json={
            'email': 'new_user@example.com',
            'password': 'password123',
            'role': 'customer'
        })
        assert response.status_code == 200
        
        # Test login
        response = client.post('/auth/login', json={
            'email': 'new_user@example.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert 'token' in response.json

def test_admin_user_creation(app, client):
    """Test admin user initialization."""
    with app.test_request_context():
        # Set test environment variables
        os.environ['ADMIN_EMAIL'] = 'admin_test@example.com'
        os.environ['ADMIN_PASSWORD'] = 'admin123'
        
        # Initialize admin user
        init_admin_user()
        
        # Try to login as admin
        response = client.post('/auth/login', json={
            'email': 'admin_test@example.com',
            'password': 'admin123'
        })
        assert response.status_code == 200
        assert 'token' in response.json
        
        # Verify admin role
        token = response.json['token']
        response = client.get('/api/admin/dashboard', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200

def test_plumber_registration(app, client):
    """Test plumber registration with profile creation."""
    with app.test_request_context():
        # Register a new plumber
        plumber_data = {
            'email': 'new_plumber@example.com',
            'password': 'password123',
            'company_name': 'Test Plumbing LLC',
            'contact_name': 'Jane Doe',
            'phone': '555-987-6543'
        }
        
        response = client.post('/auth/register/plumber', json=plumber_data)
        assert response.status_code == 200
        
        # Login as plumber
        response = client.post('/auth/login', json={
            'email': plumber_data['email'],
            'password': plumber_data['password']
        })
        assert response.status_code == 200
        token = response.json['token']
        
        # Verify plumber profile
        response = client.get('/api/plumber/profile', headers={
            'Authorization': f'Bearer {token}'
        })
        assert response.status_code == 200
        profile = response.json
        assert profile['company_name'] == plumber_data['company_name']
        assert profile['contact_name'] == plumber_data['contact_name']

def test_login_with_invalid_credentials(app, client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_password_reset_request(app, client, test_user):
    """Test password reset request functionality."""
    response = client.post('/auth/reset-password', json={
        'email': test_user['email']
    })
    assert response.status_code == 200

def test_logout_flow(app, client, test_user):
    """Test complete logout flow."""
    # First login
    response = client.post('/auth/login', json={
        'email': test_user['email'],
        'password': 'password123'
    })
    assert response.status_code == 200
    token = response.json['token']
    
    # Test accessing a protected route
    response = client.get('/api/profile', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    
    # Test logout
    response = client.post('/auth/logout', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    
    # Verify can't access protected route after logout
    response = client.get('/api/profile', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 401
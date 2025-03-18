import pytest
import os
from flask import session
from app.services.auth_service import init_admin_user, login, signup, logout, reset_password_request
from app.services.supabase import get_supabase

def test_signup_and_login(app, client):
    """Test user signup and login functionality."""
    with app.test_request_context():
        # Test signup
        response = client.post('/auth/register/plumber', data={
            'email': 'new_user@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'phone': '555-123-4567'
        })
        assert response.status_code == 200
        
        # Test login
        response = client.post('/auth/login', data={
            'email': 'new_user@example.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert 'token' in session

def test_admin_user_creation(app, client):
    """Test admin user initialization."""
    with app.test_request_context():
        # Set test environment variables
        os.environ['ADMIN_EMAIL'] = 'admin_test@example.com'
        os.environ['ADMIN_PASSWORD'] = 'admin123'
        
        # Initialize admin user
        init_admin_user()
        
        # Try to login as admin
        response = client.post('/auth/login', data={
            'email': 'admin_test@example.com',
            'password': 'admin123'
        })
        assert response.status_code == 200
        assert 'token' in session

def test_plumber_registration(app, client):
    """Test plumber registration with profile creation."""
    with app.test_request_context():
        # Register a new plumber
        plumber_data = {
            'email': 'new_plumber@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'company_name': 'Test Plumbing LLC',
            'contact_name': 'Jane Doe',
            'phone': '555-987-6543'
        }
        
        response = client.post('/auth/register/plumber', data=plumber_data)
        assert response.status_code == 200
        
        # Login as plumber
        response = client.post('/auth/login', data={
            'email': plumber_data['email'],
            'password': plumber_data['password']
        })
        assert response.status_code == 200
        assert 'token' in session
        
        # Verify plumber profile
        response = client.get('/api/plumber/profile', headers={
            'Authorization': f'Bearer {session["token"]}'
        })
        assert response.status_code == 200
        profile = response.json
        assert profile['company_name'] == plumber_data['company_name']
        assert profile['contact_name'] == plumber_data['contact_name']

def test_login_with_invalid_credentials(app, client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_password_reset_request(app, client, test_user):
    """Test password reset request functionality."""
    response = client.post('/auth/reset-password', data={
        'email': test_user['email']
    })
    assert response.status_code == 200

def test_logout_flow(app, client, test_user):
    """Test complete logout flow."""
    # First login
    response = client.post('/auth/login', data={
        'email': test_user['email'],
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in session
    
    # Test accessing a protected route
    response = client.get('/api/profile', headers={
        'Authorization': f'Bearer {session["token"]}'
    })
    assert response.status_code == 200
    
    # Test logout
    response = client.get('/auth/logout')
    assert response.status_code == 200
    assert 'token' not in session
    
    # Verify can't access protected route after logout
    response = client.get('/api/profile', headers={
        'Authorization': f'Bearer {session.get("token", "")}'
    })
    assert response.status_code == 401

def test_plumber_registration_flow(app, client):
    """Test the complete plumber registration flow."""
    with app.test_request_context():
        # Test registration page loads
        response = client.get('/auth/register/plumber')
        assert response.status_code == 200
        
        # Test successful registration redirects
        response = client.post('/auth/register/plumber', data={
            'email': 'test_plumber@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'company_name': 'Test Plumbing LLC',
            'contact_name': 'John Doe',
            'phone': '555-123-4567'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Registration successful' in response.data

def test_login_page(app, client):
    """Test login page functionality."""
    # Test login page loads
    response = client.get('/auth/login')
    assert response.status_code == 200
    
    # Test login with invalid credentials shows error
    response = client.post('/auth/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_password_reset_flow(app, client):
    """Test password reset request flow."""
    # Test reset password page loads
    response = client.get('/auth/reset-password')
    assert response.status_code == 200
    
    # Test submitting reset password request
    response = client.post('/auth/reset-password', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password reset instructions' in response.data

def test_logout_flow(app, client, test_plumber):
    """Test logout functionality."""
    # First ensure we're logged in
    with client:
        client.get('/')  # Establish session
        
        # Test logout redirects to home
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data.lower()
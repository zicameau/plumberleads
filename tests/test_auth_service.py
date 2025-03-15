import pytest
import os
import sys
from flask import session, g
from app.services.auth_service import init_admin_user, login, signup, logout, reset_password_request
from app.models.base import db, User, UserRole

# Add the parent directory to sys.path to allow importing from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_init_admin_user(app, monkeypatch):
    """Test admin user initialization."""
    # Set environment variables for testing
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin123')
    
    with app.app_context():
        # Delete admin user if it exists
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if admin_user:
            db.session.delete(admin_user)
            db.session.commit()
        
        # Initialize admin user
        init_admin_user()
        
        # Check if admin user was created
        admin_user = User.query.filter_by(email='admin@example.com').first()
        assert admin_user is not None
        assert admin_user.role == UserRole.admin

def test_admin_login(app, client, monkeypatch):
    """Test admin login functionality."""
    # Set environment variables for testing
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin123')
    
    with app.app_context():
        # Initialize admin user
        init_admin_user()
        
        # Test login with admin credentials
        response = client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'admin123'
        }, follow_redirects=True)
        
        # Check if login was successful
        assert response.status_code == 200
        
        # Check if we were redirected to the admin dashboard
        assert b'Admin Dashboard' in response.data or b'Dashboard' in response.data

def test_user_signup_and_login(app, client):
    """Test user signup and login functionality."""
    # Test user signup
    response = client.post('/auth/register/plumber', data={
        'email': 'test_plumber@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'company_name': 'Test Plumbing Co.'
    }, follow_redirects=True)
    
    # Check if signup was successful
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    # Test login with new user credentials
    response = client.post('/auth/login', data={
        'email': 'test_plumber@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Check if login was successful
    assert response.status_code == 200
    
    # Check if we were redirected to the plumber dashboard
    assert b'Plumber Dashboard' in response.data or b'Dashboard' in response.data

def test_logout(app, client):
    """Test logout functionality."""
    # First login
    response = client.post('/auth/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    }, follow_redirects=True)
    
    # Check if login was successful
    assert response.status_code == 200
    
    # Now logout
    response = client.get('/auth/logout', follow_redirects=True)
    
    # Check if logout was successful
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    
    # Try to access a protected route
    response = client.get('/admin/dashboard', follow_redirects=True)
    
    # Should be redirected to login page
    assert b'Please log in' in response.data

def test_reset_password(app, client):
    """Test password reset functionality."""
    # Test password reset request
    response = client.post('/auth/reset-password', data={
        'email': 'admin@example.com'
    }, follow_redirects=True)
    
    # Check if request was successful
    assert response.status_code == 200
    assert b'Password reset instructions' in response.data

def test_direct_auth_service_functions(app):
    """Test auth service functions directly."""
    with app.app_context():
        # Test signup function
        user = signup('test_direct@example.com', 'password123', {'role': 'plumber'})
        assert user is not None
        assert user.email == 'test_direct@example.com'
        
        # Test login function
        result = login('test_direct@example.com', 'password123')
        assert result is not None
        assert result['user'] is not None
        assert result['session'] is not None
        
        # Test logout function
        assert logout(result['session'].access_token) is True
        
        # Test reset password function
        assert reset_password_request('test_direct@example.com') is True
import pytest
import os
from flask import session, g
from app.services.auth_service import init_admin_user, login, signup, logout, reset_password_request

def test_signup_and_login(supabase, app, admin_headers):
    """Test user signup and login functionality."""
    with app.test_request_context():
        # Test signup
        user = signup('new_user@example.com', 'password123', {
            'role': 'plumber',
            'company_name': 'New Plumbing Co.'
        })
        
        assert user is not None
        assert user.email == 'new_user@example.com'
        assert user.user_metadata.get('role') == 'plumber'
        
        # Test login
        auth_response = login('new_user@example.com', 'password123')
        assert auth_response is not None
        assert auth_response.user is not None
        assert auth_response.session is not None
        
        # Cleanup
        import requests
        requests.delete(
            f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users/{user.id}",
            headers=admin_headers
        )

def test_admin_user_creation(app, admin_headers):
    """Test admin user initialization."""
    with app.test_request_context():
        # Set test environment variables
        os.environ['ADMIN_EMAIL'] = 'admin_test@example.com'
        os.environ['ADMIN_PASSWORD'] = 'admin123'
        
        # Initialize admin user
        init_admin_user()
        
        # Try to login as admin
        auth_response = login('admin_test@example.com', 'admin123')
        assert auth_response is not None
        assert auth_response.user is not None
        assert auth_response.user.user_metadata.get('role') == 'admin'
        
        # Cleanup
        import requests
        requests.delete(
            f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users/{auth_response.user.id}",
            headers=admin_headers
        )

def test_plumber_registration(supabase, app, admin_headers):
    """Test plumber registration with profile creation."""
    with app.test_request_context():
        # Register a new plumber
        plumber_data = {
            'role': 'plumber',
            'company_name': 'Test Plumbing LLC',
            'contact_name': 'Jane Doe',
            'phone': '555-987-6543'
        }
        
        user = signup('new_plumber@example.com', 'password123', plumber_data)
        assert user is not None
        
        # Verify plumber profile was created
        result = supabase.table('plumbers').select('*').eq('user_id', user.id).execute()
        assert len(result.data) == 1
        profile = result.data[0]
        assert profile['company_name'] == plumber_data['company_name']
        assert profile['contact_name'] == plumber_data['contact_name']
        
        # Cleanup
        # First delete plumber profile
        supabase.table('plumbers').delete().eq('user_id', user.id).execute()
        
        # Then delete user
        import requests
        requests.delete(
            f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users/{user.id}",
            headers=admin_headers
        )

def test_login_with_invalid_credentials(app):
    """Test login with invalid credentials."""
    with app.test_request_context():
        auth_response = login('nonexistent@example.com', 'wrongpassword')
        assert auth_response is None

def test_password_reset_request(app, admin_headers):
    """Test password reset request functionality."""
    with app.test_request_context():
        # Create a test user first
        import requests
        response = requests.post(
            f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users",
            headers=admin_headers,
            json={
                'email': 'reset_test@example.com',
                'password': 'password123',
                'email_confirm': True
            }
        )
        response.raise_for_status()
        user_data = response.json()
        
        # Test password reset request
        result = reset_password_request('reset_test@example.com')
        assert result is True
        
        # Cleanup
        requests.delete(
            f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users/{user_data['id']}",
            headers=admin_headers
        )

def test_logout_flow(supabase, app, client, test_user):
    """Test complete logout flow."""
    # First login through the API
    response = client.post('/auth/login', json={
        'email': test_user['email'],
        'password': 'password123'
    })
    assert response.status_code == 200
    
    # Get the session token from the response
    token = response.json.get('token')
    assert token is not None
    
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
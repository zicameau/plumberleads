import pytest
from app.models.plumber import Plumber
from app.models.base import User, UserRole
from app.services.auth_service import signup, login
from app import db

def test_plumber_registration_and_sync(app, client):
    """Test that plumber registration creates both user and plumber records."""
    # Test data
    test_data = {
        'email': 'test_plumber@example.com',
        'password': 'password123',
        'company_name': 'Test Plumbing Co.',
        'contact_name': 'John Doe',
        'phone': '555-123-4567'
    }
    
    # Register plumber
    response = client.post('/auth/register/plumber', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify user was created
    with app.app_context():
        user = User.query.filter_by(email=test_data['email']).first()
        assert user is not None
        assert user.role == UserRole.plumber
        
        # Verify plumber profile was created
        plumber = Plumber.get_by_user_id(user.id)
        assert plumber is not None
        assert plumber.company_name == test_data['company_name']
        assert plumber.contact_name == test_data['contact_name']
        assert plumber.phone == test_data['phone']

def test_plumber_login_and_profile_retrieval(app, client):
    """Test that plumber login retrieves the correct profile."""
    # First register a plumber
    test_data = {
        'email': 'login_test@example.com',
        'password': 'password123',
        'company_name': 'Login Test Plumbing'
    }
    
    response = client.post('/auth/register/plumber', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Log out
    client.get('/auth/logout')
    
    # Log in
    response = client.post('/auth/login', data={
        'email': test_data['email'],
        'password': test_data['password']
    }, follow_redirects=True)
    
    # Should redirect to dashboard, not profile completion
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    assert b'Complete Your Profile' not in response.data

def test_plumber_profile_update(app, client):
    """Test updating plumber profile data."""
    # Register and login a plumber
    test_data = {
        'email': 'update_test@example.com',
        'password': 'password123',
        'company_name': 'Update Test Plumbing'
    }
    
    response = client.post('/auth/register/plumber', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Update profile
    update_data = {
        'company_name': 'Updated Plumbing Co.',
        'contact_name': 'Jane Doe',
        'phone': '555-987-6543'
    }
    
    response = client.post('/plumber/profile/update', data=update_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify update in database
    with app.app_context():
        user = User.query.filter_by(email=test_data['email']).first()
        plumber = Plumber.get_by_user_id(user.id)
        assert plumber.company_name == update_data['company_name']
        assert plumber.contact_name == update_data['contact_name']
        assert plumber.phone == update_data['phone']

def test_plumber_data_persistence(app, client):
    """Test that plumber data persists between sessions."""
    # Register a plumber
    test_data = {
        'email': 'persist_test@example.com',
        'password': 'password123',
        'company_name': 'Persist Test Plumbing'
    }
    
    response = client.post('/auth/register/plumber', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Log out
    client.get('/auth/logout')
    
    # Log back in
    response = client.post('/auth/login', data={
        'email': test_data['email'],
        'password': test_data['password']
    }, follow_redirects=True)
    
    # Verify data is still there
    with app.app_context():
        user = User.query.filter_by(email=test_data['email']).first()
        plumber = Plumber.get_by_user_id(user.id)
        assert plumber.company_name == test_data['company_name'] 
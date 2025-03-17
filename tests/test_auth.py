import pytest
from flask import session
from app.models.plumber import Plumber
from app.services.mock.supabase_mock import MockUser

def test_plumber_registration(client):
    """Test plumber registration process."""
    data = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
        'company_name': 'Test Plumbing',
        'contact_name': 'John Doe',
        'phone': '1234567890',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345',
        'service_radius': '25',
        'services_offered': ['residential', 'commercial'],
        'license_number': '12345',
        'is_insured': 'yes'
    }
    
    response = client.post('/auth/register/plumber', data=data)
    assert response.status_code == 302
    assert response.location == '/auth/registration-success'
    
    # Check that plumber was created
    plumber = Plumber.get_by_email(data['email'])
    assert plumber is not None
    assert plumber.company_name == data['company_name']
    assert plumber.contact_name == data['contact_name']
    assert plumber.email == data['email']
    assert plumber.phone == data['phone']
    assert plumber.address == data['address']
    assert plumber.city == data['city']
    assert plumber.state == data['state']
    assert plumber.zip_code == data['zip_code']
    assert plumber.service_radius == int(data['service_radius'])
    assert plumber.services_offered == data['services_offered']
    assert plumber.license_number == data['license_number']
    assert plumber.is_insured is True

def test_plumber_registration_duplicate_email(client):
    """Test plumber registration with duplicate email."""
    data = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
        'company_name': 'Test Plumbing',
        'contact_name': 'John Doe',
        'phone': '1234567890',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345',
        'service_radius': '25',
        'services_offered': ['residential', 'commercial'],
        'license_number': '12345',
        'is_insured': 'yes'
    }
    
    # Register first plumber
    response = client.post('/auth/register/plumber', data=data)
    assert response.status_code == 302
    assert response.location == '/auth/registration-success'
    
    # Try to register second plumber with same email
    response = client.post('/auth/register/plumber', data=data)
    assert response.status_code == 200
    assert b'Registration failed' in response.data

def test_plumber_registration_missing_fields(client):
    """Test plumber registration with missing required fields."""
    data = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
        'company_name': 'Test Plumbing',
        'contact_name': 'John Doe',
        'phone': '1234567890',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345',
        'service_radius': '25',
        'services_offered': ['residential', 'commercial'],
        'license_number': '12345',
        'is_insured': 'yes'
    }
    
    # Remove required field
    del data['company_name']
    
    response = client.post('/auth/register/plumber', data=data)
    assert response.status_code == 200
    assert b'All required fields must be filled out' in response.data

def test_plumber_registration_password_mismatch(client):
    """Test plumber registration with mismatched passwords."""
    data = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'wrongpassword',
        'company_name': 'Test Plumbing',
        'contact_name': 'John Doe',
        'phone': '1234567890',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345',
        'service_radius': '25',
        'services_offered': ['residential', 'commercial'],
        'license_number': '12345',
        'is_insured': 'yes'
    }
    
    response = client.post('/auth/register/plumber', data=data)
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data

def test_plumber_registration_invalid_address(client):
    """Test plumber registration with invalid address."""
    data = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
        'company_name': 'Test Plumbing',
        'contact_name': 'John Doe',
        'phone': '1234567890',
        'address': 'Invalid Address',
        'city': 'Invalid City',
        'state': 'XX',
        'zip_code': '00000',
        'service_radius': '25',
        'services_offered': ['residential', 'commercial'],
        'license_number': '12345',
        'is_insured': 'yes'
    }
    
    response = client.post('/auth/register/plumber', data=data)
    assert response.status_code == 200
    assert b'Invalid address' in response.data

def test_login_success(client):
    """Test successful login."""
    # Register a plumber first
    data = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
        'company_name': 'Test Plumbing',
        'contact_name': 'John Doe',
        'phone': '1234567890',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345',
        'service_radius': '25',
        'services_offered': ['residential', 'commercial'],
        'license_number': '12345',
        'is_insured': 'yes'
    }
    
    client.post('/auth/register/plumber', data=data)
    
    # Try to login
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword'
    }
    
    response = client.post('/auth/login', data=login_data)
    assert response.status_code == 302
    assert response.location == '/'
    assert 'user_id' in session

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }
    
    response = client.post('/auth/login', data=login_data)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data
    assert 'user_id' not in session

def test_logout(client):
    """Test logout process."""
    # Login first
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword'
    }
    
    client.post('/auth/login', data=login_data)
    assert 'user_id' in session
    
    # Logout
    response = client.get('/auth/logout')
    assert response.status_code == 302
    assert response.location == '/'
    assert 'user_id' not in session

def test_reset_password(client):
    """Test password reset request."""
    data = {
        'email': 'test@example.com'
    }
    
    response = client.post('/auth/reset-password', data=data)
    assert response.status_code == 302
    assert response.location == '/auth/login'
    assert b'Password reset instructions have been sent to your email' in response.data 
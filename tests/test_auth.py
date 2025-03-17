import pytest
from app.models.plumber import Plumber
from app.models.base import db
from app.services.auth_service import signup
import uuid

def test_plumber_registration_database_creation(client, app, db):
    """Test that plumber registration properly creates both user and plumber records."""
    
    with app.app_context():
        # Test registration data
        registration_data = {
            'email': 'test.plumber@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!',
            'company_name': 'Test Plumbing Co',
            'contact_name': 'John Doe',
            'phone': '555-123-4567',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'service_radius': '25',
            'services_offered': ['emergency', 'leak', 'drain'],
            'license_number': 'PL12345',
            'is_insured': 'yes'
        }

        # Make registration request
        response = client.post('/auth/register/plumber', data=registration_data)
        
        # Check redirect to success page
        assert response.status_code == 302
        assert 'registration_success' in response.headers['Location']

        # Query the database directly to verify plumber creation
        plumber = db.query(Plumber).filter_by(email=registration_data['email']).first()
        
        # Verify plumber record exists
        assert plumber is not None, "Plumber record was not created in database"
        
        # Verify all plumber data was saved correctly
        assert plumber.company_name == registration_data['company_name']
        assert plumber.contact_name == registration_data['contact_name']
        assert plumber.email == registration_data['email']
        assert plumber.phone == registration_data['phone']
        assert plumber.address == registration_data['address']
        assert plumber.city == registration_data['city']
        assert plumber.state == registration_data['state']
        assert plumber.zip_code == registration_data['zip_code']
        assert plumber.service_radius == int(registration_data['service_radius'])
        assert set(plumber.services_offered) == set(registration_data['services_offered'])
        assert plumber.license_number == registration_data['license_number']
        assert plumber.is_insured == (registration_data['is_insured'] == 'yes')
        
        # Verify default values
        assert plumber.subscription_status == 'inactive'
        assert plumber.lead_credits == 0
        assert plumber.is_active == True
        
        # Verify user_id was set and is a valid UUID
        assert plumber.user_id is not None
        try:
            uuid.UUID(str(plumber.user_id))
        except ValueError:
            pytest.fail("user_id is not a valid UUID")

def test_plumber_registration_duplicate_email(client, app, db):
    """Test that registration fails with duplicate email."""
    
    with app.app_context():
        # Register first plumber
        registration_data = {
            'email': 'duplicate@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!',
            'company_name': 'First Plumbing Co',
            'contact_name': 'John Doe',
            'phone': '555-123-4567',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'service_radius': '25',
            'services_offered': ['emergency'],
            'license_number': 'PL12345',
            'is_insured': 'yes'
        }

        # First registration should succeed
        response = client.post('/auth/register/plumber', data=registration_data)
        assert response.status_code == 302
        
        # Attempt to register second plumber with same email
        registration_data['company_name'] = 'Second Plumbing Co'
        response = client.post('/auth/register/plumber', data=registration_data)
        
        # Should stay on registration page with error
        assert response.status_code == 200
        assert b'This email may already be registered' in response.data
        
        # Verify only one plumber exists with this email
        plumber_count = db.query(Plumber).filter_by(email=registration_data['email']).count()
        assert plumber_count == 1

def test_plumber_registration_missing_required_fields(client, app, db):
    """Test that registration fails when required fields are missing."""
    
    with app.app_context():
        # Test registration with missing required fields
        registration_data = {
            'email': 'test.plumber@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!',
            # Missing company_name and other required fields
        }

        response = client.post('/auth/register/plumber', data=registration_data)
        
        # Should stay on registration page with error
        assert response.status_code == 200
        assert b'All required fields must be filled out' in response.data
        
        # Verify no plumber was created
        plumber_count = db.query(Plumber).count()
        assert plumber_count == 0

def test_plumber_registration_invalid_password_confirmation(client, app, db):
    """Test that registration fails when passwords don't match."""
    
    with app.app_context():
        registration_data = {
            'email': 'test.plumber@example.com',
            'password': 'TestPassword123!',
            'confirm_password': 'DifferentPassword123!',
            'company_name': 'Test Plumbing Co',
            'contact_name': 'John Doe',
            'phone': '555-123-4567',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'service_radius': '25',
            'services_offered': ['emergency'],
            'license_number': 'PL12345',
            'is_insured': 'yes'
        }

        response = client.post('/auth/register/plumber', data=registration_data)
        
        # Should stay on registration page with error
        assert response.status_code == 200
        assert b'Passwords do not match' in response.data
        
        # Verify no plumber was created
        plumber_count = db.query(Plumber).count()
        assert plumber_count == 0

def test_plumber_registration_invalid_address(client, db, mocker):
    """Test plumber registration fails when address geocoding fails."""
    
    # Mock geocoding to fail
    mock_geocode = mocker.patch('app.services.lead_service.geocode_address')
    mock_geocode.side_effect = Exception('Geocoding failed')

    # Test registration data
    registration_data = {
        'email': 'test.plumber@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        'company_name': 'Test Plumbing Co',
        'contact_name': 'John Doe',
        'phone': '555-123-4567',
        'address': 'Invalid Address',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345',
        'service_radius': '25',
        'services_offered': ['emergency'],
        'license_number': 'PL12345',
        'is_insured': 'yes'
    }

    # Make registration request
    response = client.post('/auth/register/plumber', data=registration_data)
    
    # Check response shows form again with error
    assert response.status_code == 200
    assert b'Could not validate your address' in response.data

    # Verify no plumber was created
    plumber = db.query(Plumber).filter_by(email=registration_data['email']).first()
    assert plumber is None 
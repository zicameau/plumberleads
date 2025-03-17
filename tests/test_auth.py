import pytest
from app.models.plumber import Plumber

def test_plumber_registration(client, db):
    """Test plumber registration creates both user and plumber profile."""
    
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

    # Verify plumber was created in database
    plumber = Plumber.query.filter_by(email=registration_data['email']).first()
    assert plumber is not None
    
    # Verify plumber data was saved correctly
    assert plumber.company_name == registration_data['company_name']
    assert plumber.contact_name == registration_data['contact_name']
    assert plumber.phone == registration_data['phone']
    assert plumber.address == registration_data['address']
    assert plumber.city == registration_data['city']
    assert plumber.state == registration_data['state']
    assert plumber.zip_code == registration_data['zip_code']
    assert plumber.service_radius == int(registration_data['service_radius'])
    assert set(plumber.services_offered) == set(registration_data['services_offered'])
    assert plumber.license_number == registration_data['license_number']
    assert plumber.is_insured == (registration_data['is_insured'] == 'yes')
    
    # Verify user_id was set
    assert plumber.user_id is not None

def test_plumber_registration_missing_required_fields(client, db):
    """Test plumber registration fails when required fields are missing."""
    
    # Test registration data with missing required fields
    registration_data = {
        'email': 'test.plumber@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        # Missing company_name and other required fields
    }

    # Make registration request
    response = client.post('/auth/register/plumber', data=registration_data)
    
    # Check response shows form again with error
    assert response.status_code == 200
    assert b'All required fields must be filled out' in response.data

    # Verify no plumber was created
    plumber = Plumber.query.filter_by(email=registration_data['email']).first()
    assert plumber is None

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
    plumber = Plumber.query.filter_by(email=registration_data['email']).first()
    assert plumber is None 
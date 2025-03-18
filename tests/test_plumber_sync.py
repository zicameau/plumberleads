import pytest
from flask import session
from app.services.supabase import get_supabase

def test_plumber_registration_and_sync(app, client):
    """Test plumber registration and profile sync."""
    # Register a new plumber
    plumber_data = {
        'email': 'sync_test@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'company_name': 'Sync Test Plumbing',
        'contact_name': 'John Sync',
        'phone': '555-999-8888'
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
    
    # Verify profile was created in Supabase
    supabase = get_supabase()
    result = supabase.from_('plumbers').select('*').eq('email', plumber_data['email']).execute()
    assert len(result.data) == 1
    profile = result.data[0]
    assert profile['company_name'] == plumber_data['company_name']
    assert profile['contact_name'] == plumber_data['contact_name']

def test_plumber_login_and_profile_retrieval(app, client, test_plumber):
    """Test plumber login and profile retrieval."""
    # Login as plumber
    response = client.post('/auth/login', data={
        'email': test_plumber['user']['email'],
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in session
    
    # Get plumber profile
    response = client.get('/api/plumber/profile', headers={
        'Authorization': f'Bearer {session["token"]}'
    })
    assert response.status_code == 200
    profile = response.json
    assert profile['company_name'] == test_plumber['profile']['company_name']
    assert profile['contact_name'] == test_plumber['profile']['contact_name']

def test_plumber_profile_update(app, client, test_plumber):
    """Test plumber profile update."""
    # Login as plumber
    response = client.post('/auth/login', data={
        'email': test_plumber['user']['email'],
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in session
    
    # Update profile
    update_data = {
        'company_name': 'Updated Test Plumbing',
        'contact_name': 'John Updated',
        'phone': '555-111-2222'
    }
    
    response = client.post('/api/plumber/profile', 
                         data=update_data,
                         headers={'Authorization': f'Bearer {session["token"]}'})
    assert response.status_code == 200
    
    # Verify update in Supabase
    supabase = get_supabase()
    result = supabase.from_('plumbers').select('*').eq('user_id', test_plumber['user']['id']).execute()
    assert len(result.data) == 1
    profile = result.data[0]
    assert profile['company_name'] == update_data['company_name']
    assert profile['contact_name'] == update_data['contact_name']
    assert profile['phone'] == update_data['phone']

def test_plumber_data_persistence(app, client):
    """Test that plumber data persists between sessions."""
    # Register a plumber
    plumber_data = {
        'email': 'persist_test@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'company_name': 'Persist Test Plumbing',
        'contact_name': 'John Persist',
        'phone': '555-777-6666'
    }
    
    response = client.post('/auth/register/plumber', data=plumber_data)
    assert response.status_code == 200
    
    # Log out
    response = client.get('/auth/logout')
    assert response.status_code == 200
    
    # Log back in
    response = client.post('/auth/login', data={
        'email': plumber_data['email'],
        'password': plumber_data['password']
    })
    assert response.status_code == 200
    assert 'token' in session
    
    # Verify data is still there
    response = client.get('/api/plumber/profile', headers={
        'Authorization': f'Bearer {session["token"]}'
    })
    assert response.status_code == 200
    profile = response.json
    assert profile['company_name'] == plumber_data['company_name']
    assert profile['contact_name'] == plumber_data['contact_name']

def test_plumber_registration_page(app, client):
    """Test plumber registration page and form."""
    # Test registration page loads
    response = client.get('/auth/register/plumber')
    assert response.status_code == 200
    assert b'Register' in response.data
    
    # Test form fields are present
    assert b'email' in response.data.lower()
    assert b'password' in response.data.lower()
    assert b'company name' in response.data.lower()
    assert b'contact name' in response.data.lower()
    assert b'phone' in response.data.lower()

def test_plumber_profile_page(app, client, test_plumber):
    """Test plumber profile page when authenticated."""
    with client:
        # Login first
        client.post('/auth/login', data={
            'email': test_plumber['user']['email'],
            'password': 'password123'
        })
        
        # Test profile page loads
        response = client.get('/api/plumber/profile')
        assert response.status_code == 200
        
        # Verify profile data is displayed
        assert test_plumber['profile']['company_name'].encode() in response.data
        assert test_plumber['profile']['contact_name'].encode() in response.data

def test_plumber_profile_update_form(app, client, test_plumber):
    """Test plumber profile update form."""
    with client:
        # Login first
        client.post('/auth/login', data={
            'email': test_plumber['user']['email'],
            'password': 'password123'
        })
        
        # Test profile update
        update_data = {
            'company_name': 'Updated Company Name',
            'contact_name': 'Updated Contact',
            'phone': '555-999-8888'
        }
        
        response = client.post('/api/plumber/profile', 
                             data=update_data,
                             follow_redirects=True)
        assert response.status_code == 200
        assert b'Profile updated successfully' in response.data 
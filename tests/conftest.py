import pytest
import os
from dotenv import load_dotenv
from app import create_app
from app.services.supabase import init_supabase, get_supabase

# Load test environment variables
load_dotenv('.env.test')

# Ensure required test environment variables are set
def pytest_configure(config):
    """Validate and setup test environment."""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SERVICE_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        pytest.exit(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Initialize Supabase with test configuration
    init_supabase(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    yield app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def supabase():
    """Get Supabase client."""
    return get_supabase()

@pytest.fixture
def test_user(supabase):
    """Create a test user for testing."""
    # Create user with admin API to ensure email is confirmed
    headers = {
        'apikey': os.getenv('SUPABASE_SERVICE_KEY'),
        'Authorization': f'Bearer {os.getenv("SUPABASE_SERVICE_KEY")}',
        'Content-Type': 'application/json'
    }
    
    import requests
    response = requests.post(
        f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users",
        headers=headers,
        json={
            'email': 'test@example.com',
            'password': 'password123',
            'email_confirm': True,
            'user_metadata': {'role': 'customer'}
        }
    )
    response.raise_for_status()
    user_data = response.json()
    
    yield user_data
    
    # Cleanup: Delete the test user
    requests.delete(
        f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users/{user_data['id']}",
        headers=headers
    )

@pytest.fixture
def test_plumber(supabase):
    """Create a test plumber for testing."""
    # Create plumber user with admin API
    headers = {
        'apikey': os.getenv('SUPABASE_SERVICE_KEY'),
        'Authorization': f'Bearer {os.getenv("SUPABASE_SERVICE_KEY")}',
        'Content-Type': 'application/json'
    }
    
    import requests
    
    # Create plumber user
    response = requests.post(
        f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users",
        headers=headers,
        json={
            'email': 'plumber@example.com',
            'password': 'password123',
            'email_confirm': True,
            'user_metadata': {'role': 'plumber'}
        }
    )
    response.raise_for_status()
    user_data = response.json()
    
    # Create plumber profile
    plumber_data = {
        'user_id': user_data['id'],
        'company_name': 'Test Plumbing Co.',
        'contact_name': 'John Doe',
        'phone': '555-123-4567',
        'email': 'plumber@example.com'
    }
    
    result = supabase.table('plumbers').insert(plumber_data).execute()
    profile_data = result.data[0] if result.data else None
    
    yield {
        'user': user_data,
        'profile': profile_data
    }
    
    # Cleanup: Delete the test plumber
    # First delete the profile
    supabase.table('plumbers').delete().eq('user_id', user_data['id']).execute()
    
    # Then delete the user
    requests.delete(
        f"{os.getenv('SUPABASE_URL')}/auth/v1/admin/users/{user_data['id']}",
        headers=headers
    ) 
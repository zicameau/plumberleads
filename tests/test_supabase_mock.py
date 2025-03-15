import pytest
import os
import sys
from app.services.mock.supabase_mock import SupabaseMock, MockUser, MockSession, AuthResponse

# Add the parent directory to sys.path to allow importing from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_supabase_mock_initialization():
    """Test initialization of the Supabase mock."""
    mock = SupabaseMock()
    assert mock is not None
    assert mock.auth is not None

def test_supabase_mock_signup():
    """Test signup functionality of the Supabase mock."""
    mock = SupabaseMock()
    
    # Test signup with minimal data
    response = mock.auth.sign_up({
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response is not None
    assert response.user is not None
    assert response.user.email == 'test@example.com'
    
    # Test signup with user metadata
    response = mock.auth.sign_up({
        'email': 'admin@example.com',
        'password': 'admin123',
        'options': {
            'data': {
                'role': 'admin',
                'name': 'Admin User'
            }
        }
    })
    
    assert response is not None
    assert response.user is not None
    assert response.user.email == 'admin@example.com'
    assert response.user.user_metadata.get('role') == 'admin'
    assert response.user.user_metadata.get('name') == 'Admin User'

def test_supabase_mock_login():
    """Test login functionality of the Supabase mock."""
    mock = SupabaseMock()
    
    # First create a user
    mock.auth.sign_up({
        'email': 'test@example.com',
        'password': 'password123',
        'options': {
            'data': {
                'role': 'plumber'
            }
        }
    })
    
    # Test login with correct credentials
    response = mock.auth.sign_in_with_password({
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response is not None
    assert response.user is not None
    assert response.session is not None
    assert response.user.email == 'test@example.com'
    assert response.user.user_metadata.get('role') == 'plumber'
    
    # Test login with admin credentials (pre-defined in mock)
    response = mock.auth.sign_in_with_password({
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    
    assert response is not None
    assert response.user is not None
    assert response.session is not None
    assert response.user.email == 'admin@example.com'
    assert response.user.user_metadata.get('role') == 'admin'

def test_supabase_mock_get_user():
    """Test get_user functionality of the Supabase mock."""
    mock = SupabaseMock()
    
    # Test get_user with admin token
    response = mock.auth.get_user('mock-token-admin')
    
    assert response is not None
    assert response.user is not None
    assert response.user.email == 'admin@example.com'
    assert response.user.user_metadata.get('role') == 'admin'
    
    # Test get_user with regular token
    response = mock.auth.get_user('mock-token-123')
    
    assert response is not None
    assert response.user is not None
    assert response.user.email == 'test@example.com'
    assert response.user.user_metadata.get('role') == 'plumber'

def test_supabase_mock_sign_out():
    """Test sign_out functionality of the Supabase mock."""
    mock = SupabaseMock()
    
    # First login to set current user
    mock.auth.sign_in_with_password({
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    
    # Test sign out
    result = mock.auth.sign_out()
    assert result is True
    assert mock.auth.current_user is None
    assert mock.auth.session is None

def test_supabase_mock_reset_password():
    """Test reset_password functionality of the Supabase mock."""
    mock = SupabaseMock()
    
    # Test reset password
    result = mock.auth.reset_password_for_email('test@example.com')
    assert result is True
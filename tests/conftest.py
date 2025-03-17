import pytest
import os
from dotenv import load_dotenv
from app import create_app
from app.services.mock.supabase_mock import SupabaseMock
from app.services.auth_service import SupabaseClient

# Load test environment variables
load_dotenv('.env.test')

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing."""
    return SupabaseMock()

@pytest.fixture(autouse=True)
def use_mock_supabase(mock_supabase):
    """Automatically use the mock Supabase client for all tests."""
    # Reset the singleton instance
    SupabaseClient._instance = None
    # Set the mock client
    SupabaseClient.get_instance().set_client(mock_supabase) 
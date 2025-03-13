import pytest
import os
import sys
from app.services.mock.supabase_mock import SupabaseMock

# Add the parent directory to sys.path to allow importing from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import fixtures that should be available to all tests
from tests.test_app import app, client 

@pytest.fixture(autouse=True)
def mock_supabase():
    """Automatically use mock Supabase for all tests."""
    return SupabaseMock() 
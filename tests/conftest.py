import pytest
import os
import sys
from app.services.mock.supabase_mock import SupabaseMock
from app.models.base import db, Base

# Add the parent directory to sys.path to allow importing from the app package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import fixtures that should be available to all tests
from tests.test_app import app, client 

@pytest.fixture(autouse=True)
def mock_supabase():
    """Automatically use mock Supabase for all tests."""
    return SupabaseMock()

@pytest.fixture(autouse=True)
def setup_database(app):
    """Set up the database for tests."""
    with app.app_context():
        # Create all tables
        Base.metadata.create_all(db.engine)
        
        # Commit the changes
        db.session.commit()
        
        yield
        
        # Clean up after the test
        db.session.remove()
        # Optionally drop all tables after tests
        # Base.metadata.drop_all(db.engine) 
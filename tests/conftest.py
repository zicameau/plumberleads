import pytest
import os
from dotenv import load_dotenv
from app import create_app
from app.models.base import db, Base
from app.services.mock.supabase_mock import SupabaseMock

# Load test environment variables
load_dotenv('.env.test')

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app('testing')
    
    # Create app context
    with app.app_context():
        # Create all tables
        Base.metadata.create_all(db.engine)
        yield app
        # Clean up after test
        db.session.remove()
        Base.metadata.drop_all(db.engine)

@pytest.fixture
def client(app):
    """Get test client."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create a new database session for a test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Create a session bound to the connection
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        
        # Replace the global session with our test session
        db.session = session
        
        yield session
        
        # Clean up
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(autouse=True)
def mock_supabase():
    """Automatically use mock Supabase for all tests."""
    return SupabaseMock() 
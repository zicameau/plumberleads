import pytest
import os
from dotenv import load_dotenv
from app import create_app
from app.models.base import db, Base
from app.services.mock.supabase_mock import SupabaseMock

# Load test environment variables
load_dotenv('.env.test')

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app('testing')
    return app

@pytest.fixture(scope='session')
def _db(app):
    """Create database for the tests."""
    with app.app_context():
        # Create all tables
        Base.metadata.create_all(db.engine)
        yield db
        # Drop all tables after tests
        Base.metadata.drop_all(db.engine)

@pytest.fixture
def db_session(_db):
    """Create a new database session for a test."""
    connection = _db.engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    session = _db.create_scoped_session(
        options={"bind": connection, "binds": {}}
    )
    
    # Replace the global session with our test session
    _db.session = session
    
    yield session
    
    # Clean up
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def db(db_session):
    """Provide the database session to tests."""
    return db_session

@pytest.fixture
def client(app):
    """Get test client."""
    return app.test_client()

@pytest.fixture(autouse=True)
def mock_supabase():
    """Automatically use mock Supabase for all tests."""
    return SupabaseMock() 
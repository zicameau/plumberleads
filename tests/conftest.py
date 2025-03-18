import pytest
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models.base import User, UserRole
from app.services.supabase import init_supabase, get_supabase
from app.services.mock.supabase_mock import SupabaseMock

# Load test environment variables
load_dotenv('.env.test')

# Initialize Supabase with test configuration before any tests run
init_supabase(
    url=os.getenv('TEST_SUPABASE_URL', 'https://your-test-project.supabase.co'),
    key=os.getenv('TEST_SUPABASE_KEY', 'your-test-anon-key'),
    testing=True
)

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    # Create all tables
    with app.app_context():
        db.create_all()
        
    yield app
    
    # Clean up after each test
    with app.app_context():
        db.session.remove()
        db.drop_all()

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
    # Initialize Supabase with the mock client
    init_supabase(
        url='https://test.supabase.co',
        key='test-key',
        testing=True
    )

@pytest.fixture
def test_user(app):
    """Create a test user for testing."""
    with app.app_context():
        user = User(
            id='test-user-id',
            email='test@example.com',
            role=UserRole.customer
        )
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_plumber(app):
    """Create a test plumber for testing."""
    with app.app_context():
        user = User(
            id='test-plumber-id',
            email='plumber@example.com',
            role=UserRole.plumber
        )
        db.session.add(user)
        db.session.commit()
        
        from app.models.plumber import Plumber
        plumber = Plumber(
            id='test-plumber-profile-id',
            user_id=user.id,
            company_name='Test Plumbing Co.',
            contact_name='John Doe',
            phone='555-123-4567'
        )
        db.session.add(plumber)
        db.session.commit()
        return plumber 
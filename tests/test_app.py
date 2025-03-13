import pytest
import os
import sys
from app import create_app

# Add mock services to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/services/mock')))

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    
    # Create an application context
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a CLI runner."""
    return app.test_cli_runner()

def test_home_page(client):
    """Test the home page."""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200

def test_login_page(client):
    """Test the login page."""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_register_page(client):
    """Test the register page."""
    response = client.get('/auth/register/plumber')
    assert response.status_code == 200

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy'}

# Add more test cases as needed 
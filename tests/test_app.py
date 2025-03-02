import pytest
from app import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    """Test that the login page loads successfully."""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_register_page(client):
    """Test that the registration page loads successfully."""
    response = client.get('/auth/register/plumber')
    assert response.status_code == 200 
import json
import pytest
from app.utils.errors import ValidationError, AuthenticationError

def test_register_success(client, mock_supabase):
    """Test successful plumber registration"""
    data = {
        "email": "test@example.com",
        "password": "secure_password",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890"
    }
    
    response = client.post('/auth/register', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result["email"] == data["email"]
    assert result["first_name"] == data["first_name"]
    assert result["last_name"] == data["last_name"]
    assert "id" in result

def test_register_missing_fields(client):
    """Test registration with missing required fields"""
    data = {
        "email": "test@example.com",
        "password": "secure_password"
    }
    
    response = client.post('/auth/register', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    assert "Missing required field" in result["error"]["message"]

def test_login_success(client, mock_supabase):
    """Test successful login"""
    data = {
        "email": "test@example.com",
        "password": "secure_password"
    }
    
    response = client.post('/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "token" in result
    assert "user" in result
    assert result["user"]["email"] == data["email"]

def test_login_missing_credentials(client):
    """Test login with missing credentials"""
    data = {"email": "test@example.com"}
    
    response = client.post('/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    assert "Email and password are required" in result["error"]["message"]

def test_logout_success(client, mock_supabase, auth_headers):
    """Test successful logout"""
    response = client.post('/auth/logout',
                          headers=auth_headers)
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["message"] == "Successfully logged out"

def test_logout_no_token(client):
    """Test logout without token"""
    response = client.post('/auth/logout')
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "No authorization header" in result["error"]["message"]

def test_logout_invalid_token_format(client):
    """Test logout with invalid token format"""
    headers = {
        'Authorization': 'InvalidFormat',
        'Content-Type': 'application/json'
    }
    
    response = client.post('/auth/logout',
                          headers=headers)
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "Invalid authorization header format" in result["error"]["message"] 
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

def test_register_with_optional_fields(client, mock_supabase):
    """Test registration with optional fields"""
    data = {
        "email": "test@example.com",
        "password": "secure_password",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890",
        "zip_code": "12345",
        "services": ["plumbing", "heating"]
    }
    
    response = client.post('/auth/register', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result["email"] == data["email"]
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

def test_register_no_data(client):
    """Test registration with no data"""
    response = client.post('/auth/register',
                          data="",
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    assert "No data provided" in result["error"]["message"]

def test_register_invalid_json(client):
    """Test registration with invalid JSON"""
    response = client.post('/auth/register',
                          data="invalid json",
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result

def test_register_auth_failure(client, mock_supabase, monkeypatch):
    """Test registration when auth fails"""
    def mock_sign_up(*args, **kwargs):
        class Response:
            user = None
        return Response()
    
    monkeypatch.setattr(mock_supabase.auth, "sign_up", mock_sign_up)
    
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
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "Failed to create user" in result["error"]["message"]

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

def test_login_no_data(client):
    """Test login with no data"""
    response = client.post('/auth/login',
                          data="",
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    assert "No data provided" in result["error"]["message"]

def test_login_invalid_json(client):
    """Test login with invalid JSON"""
    response = client.post('/auth/login',
                          data="invalid json",
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result

def test_login_auth_failure(client, mock_supabase, monkeypatch):
    """Test login when auth fails"""
    def mock_sign_in(*args, **kwargs):
        class Response:
            user = None
            session = None
        return Response()
    
    monkeypatch.setattr(mock_supabase.auth, "sign_in_with_password", mock_sign_in)
    
    data = {
        "email": "test@example.com",
        "password": "wrong_password"
    }
    
    response = client.post('/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "Invalid credentials" in result["error"]["message"]

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

def test_logout_auth_failure(client, mock_supabase, auth_headers, monkeypatch):
    """Test logout when auth fails"""
    def mock_sign_out(*args, **kwargs):
        raise Exception("Auth service error")
    
    monkeypatch.setattr(mock_supabase.auth, "sign_out", mock_sign_out)
    
    response = client.post('/auth/logout',
                          headers=auth_headers)
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "Auth service error" in result["error"]["message"]

def test_verify_token_success(client, mock_supabase):
    """Test successful token verification"""
    token = "test_token"
    user = mock_supabase.auth.get_user(token)
    assert user is not None
    assert user.id == "test_user_id"
    assert user.email == "test@example.com"

def test_verify_token_invalid(client, mock_supabase):
    """Test invalid token verification"""
    token = "invalid_token"
    with pytest.raises(Exception) as exc_info:
        mock_supabase.auth.get_user(token)
    assert "Invalid token" in str(exc_info.value)

def test_protected_route_no_token(client):
    """Test accessing protected route without token"""
    response = client.get('/api/v1/protected')
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "No authorization header" in result["error"]["message"]

def test_protected_route_success(client, mock_supabase, auth_headers):
    """Test accessing protected route with valid token"""
    response = client.get('/api/v1/protected',
                         headers=auth_headers)
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["message"] == "Access granted"

def test_protected_route_invalid_token(client):
    """Test accessing protected route with invalid token"""
    headers = {
        'Authorization': 'Bearer invalid_token',
        'Content-Type': 'application/json'
    }
    
    response = client.get('/api/v1/protected',
                         headers=headers)
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "Invalid token" in str(result["error"]["message"])

def test_protected_route_malformed_token(client):
    """Test accessing protected route with malformed token"""
    headers = {
        'Authorization': 'malformed_token',
        'Content-Type': 'application/json'
    }
    
    response = client.get('/api/v1/protected',
                         headers=headers)
    
    assert response.status_code == 401
    result = json.loads(response.data)
    assert "error" in result
    assert "Invalid authorization header format" in result["error"]["message"] 
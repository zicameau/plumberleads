import json
import pytest
from app.utils.errors import ValidationError, NotFoundError

def test_create_lead_success(client, auth_headers):
    """Test successful lead creation"""
    data = {
        "name": "Test Customer",
        "email": "customer@example.com",
        "phone_number": "+1234567890",
        "description": "Need help with leaky faucet",
        "zip_code": "12345"
    }
    
    response = client.post('/api/v1/leads',
                          headers=auth_headers,
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    result = json.loads(response.data)
    assert result["name"] == data["name"]
    assert result["email"] == data["email"]
    assert result["status"] == "new"

def test_create_lead_missing_fields(client, auth_headers):
    """Test lead creation with missing fields"""
    data = {
        "name": "Test Customer",
        "email": "customer@example.com"
    }
    
    response = client.post('/api/v1/leads',
                          headers=auth_headers,
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    assert "Missing required field" in result["error"]["message"]

def test_get_lead_success(client, auth_headers, mock_supabase):
    """Test getting a lead by ID"""
    response = client.get('/api/v1/leads/test_lead_id',
                         headers=auth_headers)
    
    assert response.status_code == 200
    result = json.loads(response.data)
    # Check if result is a list or a dictionary
    if isinstance(result, list):
        assert result[0]["id"] == "test_lead_id"
    else:
        assert result["id"] == "test_lead_id"

def test_get_lead_not_found(client, auth_headers, mock_supabase, monkeypatch):
    """Test getting a non-existent lead"""
    def mock_execute(*args, **kwargs):
        class Response:
            data = None
        return Response()
    
    monkeypatch.setattr(mock_supabase.table("leads"), "execute", mock_execute)
    
    response = client.get('/api/v1/leads/nonexistent',
                         headers=auth_headers)
    
    assert response.status_code == 404
    result = json.loads(response.data)
    assert "error" in result
    assert "not found" in result["error"]["message"].lower()

def test_update_lead_success(client, auth_headers):
    """Test successful lead update"""
    data = {
        "description": "Updated description",
        "status": "in_progress"
    }
    
    response = client.put('/api/v1/leads/test_lead_id',
                         headers=auth_headers,
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["description"] == data["description"]
    assert result["status"] == data["status"]

def test_list_leads_success(client, auth_headers):
    """Test listing leads with pagination"""
    response = client.get('/api/v1/leads?page=1&per_page=10',
                         headers=auth_headers)
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "leads" in result
    assert "pagination" in result
    assert result["pagination"]["page"] == 1
    assert result["pagination"]["per_page"] == 10

def test_list_leads_with_filters(client, auth_headers):
    """Test listing leads with filters"""
    response = client.get('/api/v1/leads?status=new&zip_code=12345',
                         headers=auth_headers)
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "leads" in result
    assert "pagination" in result

def test_assign_lead_success(client, auth_headers):
    """Test assigning a lead to a plumber"""
    data = {
        "plumber_id": "test_plumber_id"
    }
    
    response = client.post('/api/v1/leads/test_lead_id/assign',
                          headers=auth_headers,
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["plumber_id"] == data["plumber_id"]
    assert result["status"] == "assigned"

def test_assign_lead_missing_plumber_id(client, auth_headers):
    """Test assigning a lead without plumber ID"""
    response = client.post('/api/v1/leads/test_lead_id/assign',
                          headers=auth_headers,
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    assert "Plumber ID is required" in result["error"]["message"]

def test_update_lead_status_success(client, auth_headers):
    """Test updating lead status"""
    data = {
        "status": "completed"
    }
    
    response = client.put('/api/v1/leads/test_lead_id/status',
                         headers=auth_headers,
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result["status"] == data["status"]

def test_update_lead_status_invalid(client, auth_headers):
    """Test updating lead status with invalid status"""
    data = {
        "status": "invalid_status"
    }
    
    response = client.put('/api/v1/leads/test_lead_id/status',
                         headers=auth_headers,
                         data=json.dumps(data),
                         content_type='application/json')
    
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    assert "Invalid status" in result["error"]["message"] 
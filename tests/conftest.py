import pytest
from flask import Flask
from app import create_app
from app.utils.supabase import supabase
from app.utils.errors import ValidationError, NotFoundError, AuthenticationError

@pytest.fixture
def app():
    """Create and configure a test Flask application instance"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SERVER_NAME': 'test.local',
        'FLASK_ENV': 'testing'
    })
    
    # Push an application context
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    return {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'application/json'
    }

@pytest.fixture(autouse=True)
def mock_supabase(monkeypatch):
    """Mock Supabase client for testing"""
    class MockSupabase:
        def __init__(self):
            self.auth = self.Auth()
            self.table_data = {
                'leads': [],
                'plumbers': [
                    {
                        'id': 'test_plumber_id',
                        'email': 'test@example.com',
                        'first_name': 'Test',
                        'last_name': 'Plumber'
                    }
                ]
            }
        
        class Auth:
            def sign_up(self, credentials):
                # Simulate user creation check for test_register_auth_failure
                if getattr(self, '_fail_sign_up', False):
                    class User:
                        def __init__(self):
                            self.id = None
                            
                    class Response:
                        def __init__(self):
                            self.user = None
                    
                    return Response()
                
                class User:
                    def __init__(self):
                        self.id = "test_user_id"
                        self.email = credentials["email"]
                
                class Session:
                    def __init__(self):
                        self.access_token = "test_token"
                
                class Response:
                    def __init__(self):
                        self.user = User()
                        self.session = Session()
                
                return Response()
            
            def sign_in_with_password(self, credentials):
                # Simulate login failure for test_login_auth_failure
                if getattr(self, '_fail_sign_in', False):
                    class User:
                        id = None
                        email = None
                    
                    class Session:
                        access_token = None
                    
                    class Response:
                        def __init__(self):
                            self.user = None
                            self.session = None
                    
                    return Response()
                
                class User:
                    def __init__(self):
                        self.id = "test_user_id"
                        self.email = credentials["email"]
                
                class Session:
                    def __init__(self):
                        self.access_token = "test_token"
                
                class Response:
                    def __init__(self):
                        self.user = User()
                        self.session = Session()
                
                return Response()
            
            def get_user(self, token):
                if token != "test_token":
                    raise Exception("Invalid token")
                
                class User:
                    def __init__(self):
                        self.id = "test_user_id"
                        self.email = "test@example.com"
                        self.role = "authenticated"
                        self.app_metadata = {"provider": "email"}
                        self.user_metadata = {}
                
                return User()
            
            def sign_out(self):
                # Simulate sign-out failure for test_logout_auth_failure
                if getattr(self, '_fail_sign_out', False):
                    raise AuthenticationError("Auth service error")
                return True
        
        def table(self, name):
            return self.Table(self.table_data, name)
        
        class Table:
            def __init__(self, table_data, name):
                self.table_data = table_data
                self.name = name
                self.conditions = []
                self._columns = "*"
                self._limit = None
                self._count = False
                self._update_data = None
                self._single = False
            
            def insert(self, data):
                if self.name not in self.table_data:
                    self.table_data[self.name] = []
                
                # Store insert data for later use
                self._insert_data = data
                
                # Validate required fields for leads
                if self.name == 'leads':
                    required_fields = ['name', 'email', 'phone_number', 'description']
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        raise ValidationError(f"Missing required field: {', '.join(missing_fields)}")
                
                data['id'] = f"test_{self.name}_id"
                self.table_data[self.name].append(data)
                return self
            
            def select(self, columns="*", count=None):
                self._columns = columns
                self._count = count == "exact"
                return self
            
            def eq(self, column, value):
                self.conditions.append((column, value))
                return self
            
            def single(self):
                self._single = True
                return self
            
            def limit(self, count):
                self._limit = count
                return self
            
            def range(self, start, end):
                self._range = (start, end)
                return self
            
            def update(self, data):
                self._update_data = data
                # Validate status update
                if self.name == 'leads' and 'status' in data:
                    valid_statuses = ['new', 'assigned', 'in_progress', 'completed', 'cancelled']
                    if data['status'] not in valid_statuses:
                        raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
                return self
            
            def execute(self):
                class Response:
                    def __init__(self, data, count=None):
                        self.data = data
                        self.count = count
                
                # For count queries
                if self._count:
                    return Response(None, count=len(self.table_data.get(self.name, [])))
                
                # For normal queries
                if self.name == 'leads':
                    # Check conditions for single lead lookup
                    if self._single and any(col == 'id' for col, _ in self.conditions):
                        lead_id = next(val for col, val in self.conditions if col == 'id')
                        if lead_id != 'test_lead_id':
                            # Return None for not found case
                            raise NotFoundError(f"Lead not found with ID: {lead_id}")
                    
                    mock_data = {
                        "id": "test_lead_id",
                        "name": "Test Customer",
                        "email": "customer@example.com",
                        "phone_number": "+1234567890",
                        "description": "Need help with leaky faucet",
                        "zip_code": "12345",
                        "status": "new",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                    
                    # If this is an update operation
                    if self._update_data:
                        # Check for status validation
                        if 'status' in self._update_data and self._update_data['status'] not in ['new', 'assigned', 'in_progress', 'completed', 'cancelled']:
                            raise ValidationError(f"Invalid status. Must be one of: new, assigned, in_progress, completed, cancelled")
                        mock_data.update(self._update_data)
                    
                    # Return single item or list based on query type
                    if self._single:
                        return Response(mock_data)
                    else:
                        return Response([mock_data])
                elif self.name == 'plumbers':
                    # Handle plumber tables
                    mock_data = {
                        "id": "test_user_id",
                        "email": "test@example.com",
                        "first_name": "Test",
                        "last_name": "User",
                        "phone_number": "+1234567890"
                    }
                    
                    # If this is an insert operation
                    if hasattr(self, '_insert_data') and self._insert_data:
                        mock_data.update(self._insert_data)
                    
                    # Return single item or list based on query type
                    if self._single:
                        return Response(mock_data)
                    else:
                        return Response([mock_data])
                else:
                    mock_data = {
                        "id": "test_user_id",
                        "email": "test@example.com",
                        "first_name": "Test",
                        "last_name": "User",
                        "phone_number": "+1234567890"
                    }
                    return Response(mock_data)
    
    mock_client = MockSupabase()
    # Patch at the utility level
    monkeypatch.setattr("app.utils.supabase.supabase", mock_client)
    
    # Patch at the service level directly
    monkeypatch.setattr("app.services.auth_service.supabase", mock_client)
    monkeypatch.setattr("app.services.lead_service.supabase", mock_client)
    
    return mock_client 
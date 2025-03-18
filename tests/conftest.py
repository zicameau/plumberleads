import pytest
from flask import Flask
from app import create_app
from app.utils.supabase import supabase

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
            self.table_data = {}
        
        class Auth:
            def sign_up(self, credentials):
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
                
                return User()
            
            def sign_out(self):
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
            
            def insert(self, data):
                if self.name not in self.table_data:
                    self.table_data[self.name] = []
                self.table_data[self.name].append(data)
                return self
            
            def select(self, columns="*"):
                self._columns = columns
                return self
            
            def eq(self, column, value):
                self.conditions.append((column, value))
                return self
            
            def single(self):
                return self
            
            def limit(self, count):
                self._limit = count
                return self
            
            def execute(self):
                class Response:
                    def __init__(self, data):
                        self.data = [data]
                
                return Response({
                    "id": "test_user_id",
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "phone_number": "+1234567890"
                })
    
    mock_client = MockSupabase()
    monkeypatch.setattr("app.services.auth_service.supabase", mock_client)
    monkeypatch.setattr("app.utils.supabase.supabase", mock_client)
    return mock_client 
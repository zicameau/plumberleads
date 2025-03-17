from datetime import datetime
import uuid

class MockUser:
    """Mock user class for testing."""
    def __init__(self, id, email, user_metadata=None):
        self.id = id
        self.email = email
        self.user_metadata = user_metadata or {}
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

class MockSession:
    """Mock session class for testing."""
    def __init__(self, access_token):
        self.access_token = access_token
        self.user = None

class SupabaseMock:
    """Mock Supabase client for testing."""
    
    def __init__(self):
        self.users = {}
        self.plumbers = {}
        self.auth = AuthMock(self)
        self.table = TableMock(self)
    
    def reset(self):
        """Reset all mock data."""
        self.users.clear()
        self.plumbers.clear()

class AuthMock:
    """Mock Supabase Auth client."""
    
    def __init__(self, supabase_mock):
        self.supabase_mock = supabase_mock
    
    def sign_up(self, data):
        """Mock user registration."""
        user_id = str(uuid.uuid4())
        user = MockUser(
            id=user_id,
            email=data['email'],
            user_metadata=data.get('options', {}).get('data', {})
        )
        self.supabase_mock.users[user_id] = user
        return AuthResponse(user)
    
    def sign_in_with_password(self, data):
        """Mock user login."""
        for user in self.supabase_mock.users.values():
            if user.email == data['email']:
                return AuthResponse(user)
        return None
    
    def sign_out(self):
        """Mock user logout."""
        return True

class TableMock:
    """Mock Supabase Table client."""
    
    def __init__(self, supabase_mock):
        self.supabase_mock = supabase_mock
    
    def __call__(self, table_name):
        self.table_name = table_name
        return self
    
    def select(self, *args):
        """Mock select query."""
        self.query_type = 'select'
        self.columns = args
        return self
    
    def insert(self, data):
        """Mock insert query."""
        self.query_type = 'insert'
        self.data = data
        return self
    
    def update(self, data):
        """Mock update query."""
        self.query_type = 'update'
        self.data = data
        return self
    
    def eq(self, column, value):
        """Mock equality filter."""
        self.filter_column = column
        self.filter_value = value
        return self
    
    def execute(self):
        """Execute the mock query."""
        if self.table_name == 'plumbers':
            if self.query_type == 'insert':
                plumber_id = str(uuid.uuid4())
                self.supabase_mock.plumbers[plumber_id] = {
                    'id': plumber_id,
                    **self.data
                }
                return QueryResponse([self.supabase_mock.plumbers[plumber_id]])
            elif self.query_type == 'select':
                if hasattr(self, 'filter_column') and self.filter_column == 'user_id':
                    for plumber in self.supabase_mock.plumbers.values():
                        if plumber['user_id'] == self.filter_value:
                            return QueryResponse([plumber])
                return QueryResponse(list(self.supabase_mock.plumbers.values()))
            elif self.query_type == 'update':
                if hasattr(self, 'filter_column') and self.filter_column == 'id':
                    plumber_id = self.filter_value
                    if plumber_id in self.supabase_mock.plumbers:
                        self.supabase_mock.plumbers[plumber_id].update(self.data)
                        return QueryResponse([self.supabase_mock.plumbers[plumber_id]])
        return QueryResponse([])

class AuthResponse:
    """Mock Auth Response."""
    
    def __init__(self, user):
        self.user = user
        self.session = MockSession('mock-token')

class QueryResponse:
    """Mock Query Response."""
    
    def __init__(self, data):
        self.data = data 
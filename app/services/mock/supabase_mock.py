from datetime import datetime, timedelta
import uuid

class MockUser:
    """Mock user class for testing."""
    def __init__(self, id=None, email=None, user_metadata=None):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.user_metadata = user_metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class MockSession:
    """Mock session class for testing."""
    def __init__(self, access_token=None, user=None):
        self.access_token = access_token or str(uuid.uuid4())
        self.user = user

class QueryResponse:
    """Mock Query Response."""
    
    def __init__(self, data=None, error=None):
        self.data = data or []
        self.error = error

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        return getattr(self, key)

class AuthMock:
    """Mock Supabase Auth client."""
    
    def __init__(self):
        self._users = {}  # email -> MockUser
        self._sessions = {}  # access_token -> MockSession
        self.current_user = None
        self.current_session = None
    
    def sign_up(self, data):
        """Mock user registration."""
        email = data.get('email')
        password = data.get('password')
        user_metadata = data.get('options', {}).get('data', {})
        
        if not email or not password:
            raise ValueError("Email and password are required")
        
        if email in self._users:
            raise ValueError("User already exists")
        
        user = MockUser(email=email, user_metadata=user_metadata)
        self._users[email] = user
        
        session = MockSession(user=user)
        self._sessions[session.access_token] = session
        
        self.current_user = user
        self.current_session = session
        
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'user_metadata': user.user_metadata,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            },
            'session': {
                'access_token': session.access_token,
                'user': user
            }
        }
    
    def sign_in(self, credentials):
        """Mock user login."""
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            raise ValueError("Email and password are required")
        
        user = self._users.get(email)
        if not user:
            raise ValueError("User not found")
        
        session = MockSession(user=user)
        self._sessions[session.access_token] = session
        
        self.current_user = user
        self.current_session = session
        
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'user_metadata': user.user_metadata,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            },
            'session': {
                'access_token': session.access_token,
                'user': user
            }
        }
    
    def sign_out(self):
        """Mock user logout."""
        if self.current_session:
            token = self.current_session.access_token
            if token in self._sessions:
                del self._sessions[token]
        self.current_user = None
        self.current_session = None
        return True

    def get_user(self):
        return self.current_user

    def reset_password_for_email(self, email):
        if email not in self._users:
            raise ValueError("User not found")
        return True

class SupabaseMock:
    """Mock Supabase client for testing."""
    
    def __init__(self):
        self.auth = AuthMock()
        self._tables = {}
    
    def table(self, name):
        if name not in self._tables:
            self._tables[name] = []
        return TableMock(self._tables[name])

    def from_(self, name):
        return self.table(name)

class TableMock:
    """Mock Supabase Table client."""
    
    def __init__(self, data):
        self._data = data
        self._filters = []
        self._selected_columns = None
    
    def insert(self, records):
        """Mock insert query."""
        if not isinstance(records, list):
            records = [records]
        for record in records:
            if 'id' not in record:
                record['id'] = str(uuid.uuid4())
            if 'created_at' not in record:
                record['created_at'] = datetime.utcnow()
            if 'updated_at' not in record:
                record['updated_at'] = datetime.utcnow()
            self._data.append(record)
        return QueryResponse(data=records)
    
    def select(self, columns='*'):
        """Mock select query."""
        self._selected_columns = columns.split(',') if isinstance(columns, str) else columns
        return self
    
    def eq(self, column, value):
        """Mock equality filter."""
        self._filters.append(lambda x: x.get(column) == value)
        return self
    
    def execute(self):
        """Execute the mock query."""
        result = self._data
        for f in self._filters:
            result = [r for r in result if f(r)]
        
        if self._selected_columns and '*' not in self._selected_columns:
            result = [{k: r[k] for k in self._selected_columns if k in r} for r in result]
        
        return QueryResponse(data=result) 
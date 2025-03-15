class SupabaseMock:
    def __init__(self):
        self.auth = AuthMock()

class AuthMock:
    def __init__(self):
        self.current_user = None
        self.session = None

    def sign_up(self, credentials):
        """Mock sign up method"""
        email = credentials.get('email')
        options = credentials.get('options', {})
        user_metadata = options.get('data', {})
        
        user = MockUser(
            id='mock-user-id',
            email=email,
            user_metadata=user_metadata
        )
        
        return AuthResponse({
            'user': user,
            'session': None
        })
    
    def sign_in_with_password(self, credentials):
        """Mock sign in method"""
        email = credentials.get('email')
        password = credentials.get('password')
        
        # For testing, accept any credentials
        user = MockUser(
            id='mock-user-id',
            email=email,
            user_metadata={'role': 'plumber'}
        )
        
        session = MockSession(
            access_token='mock-access-token',
            refresh_token='mock-refresh-token',
            user=user
        )
        
        return AuthResponse({
            'user': user,
            'session': session
        })
    
    def get_user(self, token):
        """Mock get user method for token verification"""
        # For testing, accept any token and return a mock user
        user = MockUser(
            id='mock-user-id',
            email='test@example.com',
            user_metadata={'role': 'plumber'}
        )
        
        return AuthResponse({
            'user': user,
            'session': None
        })
    
    def sign_out(self):
        """Mock sign out method"""
        self.current_user = None
        self.session = None
        return True
    
    def reset_password_for_email(self, email):
        """Mock reset password method"""
        # Just return success for testing
        return True

class MockUser:
    def __init__(self, id, email, user_metadata=None):
        self.id = id
        self.email = email
        self.user_metadata = user_metadata or {}

class MockSession:
    def __init__(self, access_token, refresh_token=None, user=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user = user

class AuthResponse:
    def __init__(self, data):
        self.user = data.get('user')
        self.session = data.get('session') 
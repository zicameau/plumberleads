class SupabaseMock:
    def __init__(self):
        self.auth = AuthMock()

class AuthMock:
    def __init__(self):
        self.current_user = None
        self.session = None
        # Store registered users for testing
        self.users = {}
        # Pre-register admin user
        admin_user = MockUser(
            id='123e4567-e89b-12d3-a456-426614174000',  # Valid UUID format
            email='admin@example.com',
            user_metadata={'role': 'admin', 'name': 'Admin User'}
        )
        self.users['admin@example.com'] = {
            'user': admin_user,
            'password': 'admin123'
        }

    def sign_up(self, credentials):
        """Mock sign up method"""
        email = credentials.get('email')
        password = credentials.get('password')
        options = credentials.get('options', {})
        user_metadata = options.get('data', {})
        
        # Generate a mock user ID in valid UUID format
        import uuid
        user_id = str(uuid.uuid4())
        if email == 'admin@example.com':
            user_id = '123e4567-e89b-12d3-a456-426614174000'  # Consistent UUID for admin
        
        user = MockUser(
            id=user_id,
            email=email,
            user_metadata=user_metadata
        )
        
        # Store user for later authentication
        self.users[email] = {
            'user': user,
            'password': password
        }
        
        return AuthResponse({
            'user': user,
            'session': None
        })
    
    def sign_in_with_password(self, credentials):
        """Mock sign in method"""
        email = credentials.get('email')
        password = credentials.get('password')
        
        # Check if user exists and password matches
        if email in self.users and self.users[email]['password'] == password:
            user = self.users[email]['user']
        elif email == 'admin@example.com' and password == 'admin123':
            # Special case for admin user
            user = MockUser(
                id='123e4567-e89b-12d3-a456-426614174000',  # Valid UUID format
                email='admin@example.com',
                user_metadata={'role': 'admin', 'name': 'Admin User'}
            )
        else:
            # For testing, accept any credentials with default plumber role
            import uuid
            user = MockUser(
                id=str(uuid.uuid4()),  # Generate a valid UUID
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
        # Special case for admin token
        if token == 'mock-token-admin':
            user = MockUser(
                id='123e4567-e89b-12d3-a456-426614174000',  # Valid UUID format
                email='admin@example.com',
                user_metadata={'role': 'admin', 'name': 'Admin User'}
            )
        else:
            # For testing, return a mock user with plumber role
            import uuid
            user = MockUser(
                id=str(uuid.uuid4()),  # Generate a valid UUID
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
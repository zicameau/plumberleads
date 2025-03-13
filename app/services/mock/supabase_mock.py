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
        return AuthResponse({
            'user': {
                'id': 'mock-user-id',
                'email': email,
                'role': 'authenticated'
            },
            'session': None
        })

class AuthResponse:
    def __init__(self, data):
        self.user = data.get('user')
        self.session = data.get('session') 
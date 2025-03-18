from flask import jsonify

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or {})
        rv['error'] = {
            'code': self.__class__.__name__.upper(),
            'message': self.message
        }
        return rv

class ValidationError(APIError):
    """Raised when input validation fails"""
    pass

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    def __init__(self, message="Authentication required", payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(APIError):
    """Raised when authorization fails"""
    def __init__(self, message="Insufficient permissions", payload=None):
        super().__init__(message, status_code=403, payload=payload)

class NotFoundError(APIError):
    """Raised when a resource is not found"""
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)

def handle_api_error(error):
    """Error handler for API errors"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response 
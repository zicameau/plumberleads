# PlumberLeads API Design Documentation

## Overview

The PlumberLeads API provides the backend functionality for the lead generation and management platform. This RESTful API is built using Python Flask and interacts with a PostgreSQL database.

## Base URL

All API endpoints are relative to:

```
https://plumberleads.com/
```

For development:

```
http://localhost:5000/
```

## Authentication

All API requests (except public endpoints) require authentication using session cookies provided by Flask-Login or via API tokens for programmatic access.

### Token Authentication

For API token authentication (used by external services):

```
Authorization: Bearer <token>
```

## API Structure

The API is organized using Flask Blueprints:

- `/auth` - Authentication endpoints
- `/api/plumbers` - Plumber profile management
- `/api/leads` - Lead management
- `/api/payments` - Payment processing
- `/api/admin` - Admin functionality
- `/webhook` - External service webhooks

## Error Handling

All errors follow a standard format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human readable message",
    "details": {}
  }
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

API requests are limited to 100 requests per minute per IP address or API key using Flask-Limiter.

## Endpoints

### Authentication

#### POST /auth/register

Register a new plumber account.

**Request:**
```json
{
  "email": "plumber@example.com",
  "password": "securepassword",
  "name": "John Smith",
  "phone": "+15551234567",
  "company": "Smith Plumbing"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_id",
    "email": "plumber@example.com",
    "name": "John Smith",
    "role": "plumber",
    "created_at": "2023-03-19T12:00:00Z"
  },
  "message": "Registration successful. Please check your email to verify your account."
}
```

#### POST /auth/login

Authenticate and receive a session cookie.

**Request:**
```json
{
  "email": "plumber@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_id",
    "email": "plumber@example.com",
    "name": "John Smith",
    "role": "plumber"
  },
  "message": "Login successful"
}
```

#### POST /auth/logout

End the current user session.

**Response:**
```json
{
  "message": "Logout successful"
}
```

#### POST /auth/password/reset-request

Request a password reset.

**Request:**
```json
{
  "email": "plumber@example.com"
}
```

**Response:**
```json
{
  "message": "If an account with that email exists, a password reset link has been sent"
}
```

#### POST /auth/password/reset

Reset password with token.

**Request:**
```json
{
  "token": "reset_token",
  "password": "new_secure_password"
}
```

**Response:**
```json
{
  "message": "Password reset successful"
}
```

#### POST /api/token

Generate an API token for external services.

**Response:**
```json
{
  "token": "api_token",
  "expires_at": "2023-04-19T12:00:00Z"
}
```

### Plumber Profile

#### GET /api/plumbers/profile

Get the current plumber's profile.

**Response:**
```json
{
  "id": "plumber_id",
  "name": "John Smith",
  "email": "plumber@example.com",
  "phone": "+15551234567", 
  "company": "Smith Plumbing",
  "profile_image": "https://example.com/profile.jpg",
  "service_areas": ["Los Angeles", "Beverly Hills"],
  "service_types": ["Emergency", "Installation", "Repair"],
  "subscription_status": "active",
  "created_at": "2023-03-19T12:00:00Z"
}
```

#### PUT /api/plumbers/profile

Update the current plumber's profile.

**Request:**
```json
{
  "name": "John D. Smith",
  "phone": "+15551234567",
  "company": "Smith Professional Plumbing",
  "profile_image": "https://example.com/new-profile.jpg",
  "service_areas": ["Los Angeles", "Beverly Hills", "Santa Monica"],
  "service_types": ["Emergency", "Installation", "Repair", "Maintenance"]
}
```

**Response:**
```json
{
  "id": "plumber_id",
  "name": "John D. Smith",
  "email": "plumber@example.com",
  "phone": "+15551234567",
  "company": "Smith Professional Plumbing",
  "profile_image": "https://example.com/new-profile.jpg",
  "service_areas": ["Los Angeles", "Beverly Hills", "Santa Monica"],
  "service_types": ["Emergency", "Installation", "Repair", "Maintenance"],
  "subscription_status": "active",
  "updated_at": "2023-03-19T14:00:00Z"
}
```

#### POST /api/plumbers/profile/image

Upload a profile image (multipart form data).

**Request:**
- Form data with 'image' field containing the file

**Response:**
```json
{
  "profile_image": "https://example.com/uploads/profile-123.jpg",
  "message": "Profile image updated successfully"
}
```

### Leads

#### GET /api/leads

Get leads available to the authenticated plumber.

**Query Parameters:**
- `status`: Filter by status (available, claimed, completed)
- `area`: Filter by service area
- `type`: Filter by service type
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 20)

**Response:**
```json
{
  "leads": [
    {
      "id": "lead_id_1",
      "service_area": "Los Angeles",
      "service_type": "Emergency",
      "description": "Pipe burst in kitchen",
      "created_at": "2023-03-19T10:00:00Z",
      "status": "available",
      "price": 20.00
    },
    {
      "id": "lead_id_2",
      "service_area": "Beverly Hills",
      "service_type": "Installation",
      "description": "New bathroom fixtures installation",
      "created_at": "2023-03-19T09:30:00Z",
      "status": "available",
      "price": 15.00
    }
  ],
  "pagination": {
    "total": 45,
    "page": 1,
    "per_page": 20,
    "pages": 3
  }
}
```

#### GET /api/leads/<lead_id>

Get details for a specific lead.

**Response:**
```json
{
  "id": "lead_id_1",
  "service_area": "Los Angeles",
  "service_type": "Emergency",
  "description": "Pipe burst in kitchen",
  "created_at": "2023-03-19T10:00:00Z",
  "status": "available",
  "price": 20.00,
  "partial_details": {
    "neighborhood": "Downtown",
    "job_size": "Medium",
    "urgency": "High"
  }
}
```

#### POST /api/leads/<lead_id>/claim

Claim a lead (initiates payment process).

**Response:**
```json
{
  "claim_id": "claim_123",
  "lead_id": "lead_id_1",
  "payment_intent": "pi_123456",
  "payment_url": "https://payment.stripe.com/123456",
  "status": "pending_payment"
}
```

#### GET /api/leads/claimed

Get all leads claimed by the authenticated plumber.

**Query Parameters:**
- `status`: Filter by status (active, completed, cancelled)
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 20)

**Response:**
```json
{
  "leads": [
    {
      "id": "lead_id_3",
      "service_area": "Santa Monica",
      "service_type": "Repair",
      "description": "Leaking faucet in bathroom",
      "created_at": "2023-03-18T15:45:00Z",
      "claimed_at": "2023-03-18T16:00:00Z",
      "status": "active",
      "customer": {
        "name": "Jane Doe",
        "phone": "+15559876543",
        "email": "jane@example.com",
        "address": "123 Main St, Santa Monica, CA"
      }
    }
  ],
  "pagination": {
    "total": 12,
    "page": 1,
    "per_page": 20,
    "pages": 1
  }
}
```

#### PUT /api/leads/claimed/<lead_id>

Update the status of a claimed lead.

**Request:**
```json
{
  "status": "completed",
  "notes": "Job completed successfully"
}
```

**Response:**
```json
{
  "id": "lead_id_3",
  "status": "completed",
  "updated_at": "2023-03-20T10:00:00Z",
  "message": "Lead status updated successfully"
}
```

#### POST /api/leads/claimed/<lead_id>/notes

Add a note to a claimed lead.

**Request:**
```json
{
  "note": "Customer prefers appointment in the morning"
}
```

**Response:**
```json
{
  "id": "note_id_1",
  "lead_id": "lead_id_3",
  "note": "Customer prefers appointment in the morning",
  "created_at": "2023-03-20T09:00:00Z"
}
```

#### POST /api/leads/claimed/<lead_id>/report

Report an issue with a claimed lead.

**Request:**
```json
{
  "issue_type": "unable_to_contact",
  "details": "Phone number seems to be incorrect"
}
```

**Response:**
```json
{
  "report_id": "report_id_1",
  "lead_id": "lead_id_3",
  "status": "pending_review",
  "message": "Report submitted successfully"
}
```

### Payments

#### GET /api/payments

Get payment history for the authenticated plumber.

**Query Parameters:**
- `status`: Filter by status (succeeded, pending, failed)
- `from_date`: Start date
- `to_date`: End date
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 20)

**Response:**
```json
{
  "payments": [
    {
      "id": "payment_id_1",
      "amount": 20.00,
      "currency": "usd",
      "status": "succeeded",
      "created_at": "2023-03-18T16:00:00Z",
      "lead_id": "lead_id_3",
      "payment_method": "card",
      "receipt_url": "https://receipt.stripe.com/123456"
    }
  ],
  "pagination": {
    "total": 8,
    "page": 1,
    "per_page": 20,
    "pages": 1
  }
}
```

#### POST /api/payments/methods

Add a new payment method.

**Request:**
```json
{
  "payment_method_id": "pm_123456",
  "set_default": true
}
```

**Response:**
```json
{
  "id": "pm_123456",
  "type": "card",
  "card": {
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2025
  },
  "is_default": true,
  "message": "Payment method added successfully"
}
```

#### GET /api/payments/methods

Get saved payment methods for the authenticated plumber.

**Response:**
```json
{
  "payment_methods": [
    {
      "id": "pm_123456",
      "type": "card",
      "card": {
        "brand": "visa",
        "last4": "4242",
        "exp_month": 12,
        "exp_year": 2025
      },
      "is_default": true
    }
  ]
}
```

#### DELETE /api/payments/methods/<method_id>

Remove a payment method.

**Response:**
```json
{
  "message": "Payment method removed successfully"
}
```

#### POST /api/payments/methods/<method_id>/default

Set a payment method as default.

**Response:**
```json
{
  "id": "pm_123456",
  "is_default": true,
  "message": "Default payment method updated"
}
```

#### POST /api/payments/refund-request

Request a refund for a lead.

**Request:**
```json
{
  "lead_id": "lead_id_3",
  "reason": "lead_quality",
  "details": "Customer information was incorrect"
}
```

**Response:**
```json
{
  "refund_request_id": "refund_req_1",
  "lead_id": "lead_id_3",
  "status": "pending_review",
  "message": "Refund request submitted successfully"
}
```

### Admin Endpoints

#### GET /api/admin/plumbers

Get all plumbers (admin only).

**Query Parameters:**
- `status`: Filter by status (active, inactive, pending)
- `search`: Search by name or email
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 20)

**Response:**
```json
{
  "plumbers": [
    {
      "id": "plumber_id_1",
      "name": "John Smith",
      "email": "john@example.com",
      "company": "Smith Plumbing",
      "service_areas": ["Los Angeles", "Beverly Hills"],
      "subscription_status": "active",
      "created_at": "2023-03-10T12:00:00Z",
      "leads_claimed": 15
    }
  ],
  "pagination": {
    "total": 35,
    "page": 1,
    "per_page": 20,
    "pages": 2
  }
}
```

#### GET /api/admin/plumbers/<plumber_id>

Get a specific plumber's details (admin only).

**Response:**
```json
{
  "id": "plumber_id_1",
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "+15551234567",
  "company": "Smith Plumbing",
  "profile_image": "https://example.com/profile.jpg",
  "service_areas": ["Los Angeles", "Beverly Hills"],
  "service_types": ["Emergency", "Installation", "Repair"],
  "subscription_status": "active",
  "created_at": "2023-03-10T12:00:00Z",
  "leads_claimed": 15,
  "payments": {
    "total": 300.00,
    "count": 15,
    "last_payment_date": "2023-03-18T16:00:00Z"
  }
}
```

#### PUT /api/admin/plumbers/<plumber_id>

Update a plumber's details (admin only).

**Request:**
```json
{
  "subscription_status": "inactive",
  "notes": "Account suspended due to payment issues"
}
```

**Response:**
```json
{
  "id": "plumber_id_1",
  "subscription_status": "inactive",
  "updated_at": "2023-03-20T10:00:00Z",
  "message": "Plumber updated successfully"
}
```

#### GET /api/admin/leads

Get all leads (admin only).

**Query Parameters:**
- `status`: Filter by status (available, claimed, completed)
- `area`: Filter by service area
- `type`: Filter by service type
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 20)

**Response:**
```json
{
  "leads": [
    {
      "id": "lead_id_1",
      "service_area": "Los Angeles",
      "service_type": "Emergency",
      "description": "Pipe burst in kitchen",
      "created_at": "2023-03-19T10:00:00Z",
      "status": "available",
      "price": 20.00,
      "source": "facebook_ads"
    }
  ],
  "pagination": {
    "total": 120,
    "page": 1,
    "per_page": 20,
    "pages": 6
  }
}
```

#### POST /api/admin/leads

Create a new lead manually (admin only).

**Request:**
```json
{
  "customer_name": "Jane Doe",
  "customer_phone": "+15559876543",
  "customer_email": "jane@example.com",
  "service_area": "Los Angeles",
  "service_type": "Emergency",
  "description": "Pipe burst in kitchen",
  "address": "123 Main St, Los Angeles, CA",
  "price": 20.00,
  "source": "manual"
}
```

**Response:**
```json
{
  "id": "lead_id_new",
  "service_area": "Los Angeles",
  "service_type": "Emergency",
  "description": "Pipe burst in kitchen",
  "created_at": "2023-03-19T16:00:00Z",
  "status": "available",
  "price": 20.00,
  "source": "manual"
}
```

#### GET /api/admin/reports

Get system reports and analytics (admin only).

**Query Parameters:**
- `report_type`: Type of report (leads, revenue, plumbers)
- `from_date`: Start date
- `to_date`: End date

**Response:**
```json
{
  "report_type": "leads",
  "from_date": "2023-03-01T00:00:00Z",
  "to_date": "2023-03-31T23:59:59Z",
  "data": {
    "total_leads": 250,
    "leads_by_status": {
      "available": 50,
      "claimed": 150,
      "completed": 45,
      "cancelled": 5
    },
    "leads_by_source": {
      "facebook_ads": 120,
      "google_ads": 85,
      "website": 25,
      "manual": 20
    },
    "leads_by_area": {
      "Los Angeles": 140,
      "Beverly Hills": 65,
      "Santa Monica": 45
    }
  }
}
```

### Webhooks

#### POST /webhook/stripe

Webhook for Stripe payment events.

**Request:**
Stripe webhook payload with signature in headers

**Response:**
```json
{
  "received": true
}
```

#### POST /webhook/leads

Webhook for receiving leads from external sources.

**Request:**
```json
{
  "api_key": "your_api_key",
  "customer_name": "Jane Doe",
  "customer_phone": "+15559876543",
  "customer_email": "jane@example.com",
  "service_area": "Los Angeles",
  "service_type": "Emergency",
  "description": "Pipe burst in kitchen",
  "address": "123 Main St, Los Angeles, CA",
  "source": "external_api"
}
```

**Response:**
```json
{
  "id": "lead_id_new",
  "status": "available",
  "received_at": "2023-03-19T16:00:00Z"
}
```

## Flask Implementation

The API is implemented using Flask Blueprints to organize endpoints by functionality:

```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.routes.auth import auth_bp
    from app.routes.plumbers import plumbers_bp
    from app.routes.leads import leads_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp
    from app.routes.webhooks import webhook_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(plumbers_bp, url_prefix='/api/plumbers')
    app.register_blueprint(leads_bp, url_prefix='/api/leads')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    
    return app
```

Example route implementation:

```python
# app/routes/leads.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Lead
from app.services import lead_service

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/', methods=['GET'])
@login_required
def get_leads():
    """Returns leads available to the authenticated plumber."""
    status = request.args.get('status', 'available')
    area = request.args.get('area')
    service_type = request.args.get('type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    leads, pagination = lead_service.get_available_leads(
        current_user, status, area, service_type, page, per_page
    )
    
    return jsonify({
        'leads': [lead.to_dict() for lead in leads],
        'pagination': pagination
    })
```

## Data Models

### User/Plumber
- id: UUID (primary key)
- email: String (unique)
- password_hash: String
- name: String
- phone: String
- company: String
- profile_image: String (URL)
- service_areas: Relationship to ServiceArea
- service_types: Relationship to ServiceType
- subscription_status: String (active, inactive, pending)
- role: String (plumber, admin)
- created_at: DateTime
- updated_at: DateTime

### Lead
- id: UUID (primary key)
- customer_name: String
- customer_phone: String
- customer_email: String
- service_area_id: Integer (foreign key)
- service_type_id: Integer (foreign key)
- description: Text
- address: String
- status: String (available, claimed, completed, cancelled)
- price: Numeric
- source: String (facebook_ads, google_ads, website, manual, external_api)
- claimed_by_id: UUID (foreign key to User)
- claimed_at: DateTime
- completed_at: DateTime
- created_at: DateTime
- updated_at: DateTime

### Payment
- id: UUID (primary key)
- user_id: UUID (foreign key to User)
- lead_id: UUID (foreign key to Lead)
- amount: Numeric
- currency: String
- status: String (succeeded, pending, failed)
- payment_intent_id: String
- payment_method_id: String
- receipt_url: String
- created_at: DateTime

### ServiceArea
- id: Integer (primary key)
- name: String
- region: String
- postal_code: String

### ServiceType
- id: Integer (primary key)
- name: String
- description: String
- base_price: Numeric

## Authentication and Authorization

### Authentication

Authentication is implemented using Flask-Login for session-based auth and custom token auth for API access.

### Authorization

Route access is controlled through decorators:

```python
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

## Security Considerations

- All forms should include CSRF protection
- Password should be hashed using Werkzeug's security functions
- Input validation using Flask-WTF or marshmallow
- Rate limiting to prevent abuse
- Secure headers using Flask-Talisman
- Proper session configuration (HTTPS only, secure, etc.)

## Testing

API endpoints should be tested using pytest. Example test:

```python
def test_get_leads(client, auth):
    # Login
    auth.login()
    
    # Get leads
    response = client.get('/api/leads/')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert 'leads' in json_data
    assert 'pagination' in json_data
``` 
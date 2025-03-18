# API Endpoints Documentation

This document outlines all the API endpoints available in the Plumber Leads Platform.

## Authentication Endpoints

### POST /api/auth/register
Register a new plumber account.
```json
{
  "request": {
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "phone_number": "string",
    "password": "string",
    "zip_code": "string",
    "services": ["string"]
  },
  "response": {
    "id": "uuid",
    "token": "string",
    "user": {
      "id": "uuid",
      "email": "string",
      "first_name": "string",
      "last_name": "string"
    }
  }
}
```

### POST /api/auth/login
Login to existing account.
```json
{
  "request": {
    "email": "string",
    "password": "string"
  },
  "response": {
    "token": "string",
    "user": {
      "id": "uuid",
      "email": "string",
      "first_name": "string",
      "last_name": "string"
    }
  }
}
```

### POST /api/auth/logout
Logout from current session.
```json
{
  "request": {},
  "response": {
    "message": "Successfully logged out"
  }
}
```

## Plumber Endpoints

### GET /api/plumbers/profile
Get current plumber's profile.
```json
{
  "response": {
    "id": "uuid",
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "phone_number": "string",
    "zip_code": "string",
    "services": ["string"],
    "stripe_customer_id": "string"
  }
}
```

### PUT /api/plumbers/profile
Update plumber's profile.
```json
{
  "request": {
    "first_name": "string",
    "last_name": "string",
    "phone_number": "string",
    "zip_code": "string",
    "services": ["string"]
  },
  "response": {
    "message": "Profile updated successfully"
  }
}
```

### GET /api/plumbers/leads
Get leads for current plumber.
```json
{
  "response": {
    "leads": [{
      "id": "uuid",
      "first_name": "string",
      "last_name": "string",
      "service_needed": "string",
      "urgency": "string",
      "status": "string",
      "created_at": "datetime"
    }]
  }
}
```

## Lead Management Endpoints

### POST /api/leads
Create a new lead (external service endpoint).
```json
{
  "request": {
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "phone_number": "string",
    "service_needed": "string",
    "urgency": "string"
  },
  "response": {
    "id": "uuid",
    "message": "Lead created successfully"
  }
}
```

### GET /api/leads/{id}
Get lead details.
```json
{
  "response": {
    "id": "uuid",
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "phone_number": "string",
    "service_needed": "string",
    "urgency": "string",
    "status": "string",
    "assigned_plumber_id": "uuid",
    "created_at": "datetime"
  }
}
```

### POST /api/leads/{id}/accept
Accept a lead.
```json
{
  "request": {},
  "response": {
    "message": "Lead accepted successfully",
    "payment_intent": {
      "client_secret": "string"
    }
  }
}
```

## Admin Endpoints

### GET /api/admin/plumbers
Get all plumbers (admin only).
```json
{
  "response": {
    "plumbers": [{
      "id": "uuid",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "phone_number": "string",
      "zip_code": "string",
      "services": ["string"],
      "created_at": "datetime"
    }]
  }
}
```

### GET /api/admin/leads
Get all leads (admin only).
```json
{
  "response": {
    "leads": [{
      "id": "uuid",
      "first_name": "string",
      "last_name": "string",
      "service_needed": "string",
      "urgency": "string",
      "status": "string",
      "assigned_plumber_id": "uuid",
      "created_at": "datetime"
    }]
  }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": ["error message"]
    }
  }
}
```

### 401 Unauthorized
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

### 403 Forbidden
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

### 404 Not Found
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
``` 
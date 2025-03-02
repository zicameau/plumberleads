# API Documentation

This document describes the REST API endpoints for the Plumber Lead Generation Website.

## Authentication

Most API endpoints require authentication using JWT tokens.

### Authentication Header

```
Authorization: Bearer YOUR_JWT_TOKEN
```

### Getting a JWT Token

```
POST /auth/api/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "success": true,
  "token": "JWT_TOKEN_STRING",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "role": "plumber"
  }
}
```

## Customer Endpoints

### Submit Service Request

```
POST /customer/api/request
```

**Request Body:**
```json
{
  "customer_name": "John Doe",
  "email": "customer@example.com",
  "phone": "555-123-4567",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "problem_description": "Leaking kitchen sink",
  "service_needed": ["leak", "sink"],
  "urgency": "today"
}
```

**Response:**
```json
{
  "success": true,
  "lead_id": "lead-uuid",
  "message": "Service request submitted successfully",
  "matching_plumbers_count": 5
}
```

### Track Service Request

```
GET /customer/api/track/{reference_code}
```

**Response:**
```json
{
  "lead": {
    "id": "lead-uuid",
    "reference_code": "PL-123456",
    "customer_name": "John Doe",
    "status": "claimed",
    "created_at": "2025-03-01T14:30:00Z",
    "service_needed": ["leak", "sink"],
    "urgency": "today"
  },
  "plumbers": [
    {
      "company_name": "Ace Plumbing",
      "contact_name": "Mike Smith",
      "phone": "555-987-6543",
      "email": "mike@aceplumbing.com",
      "claimed_at": "2025-03-01T15:05:22Z",
      "status": "contacted"
    }
  ]
}
```

## Plumber Endpoints

### Get Plumber Profile

```
GET /plumber/api/profile
```

**Response:**
```json
{
  "id": "plumber-uuid",
  "company_name": "Ace Plumbing",
  "contact_name": "Mike Smith",
  "email": "mike@aceplumbing.com",
  "phone": "555-987-6543",
  "address": "456 Oak St",
  "city": "New York",
  "state": "NY",
  "zip_code": "10002",
  "service_radius": 25,
  "services_offered": ["emergency", "leak", "drain", "sink"],
  "license_number": "NY-123456",
  "is_insured": true,
  "subscription_status": "active",
  "lead_credits": 10
}
```

### Update Plumber Profile

```
PUT /plumber/api/profile
```

**Request Body:**
```json
{
  "company_name": "Ace Plumbing Services",
  "contact_name": "Michael Smith",
  "phone": "555-987-6543",
  "address": "456 Oak St",
  "city": "New York",
  "state": "NY",
  "zip_code": "10002",
  "service_radius": 30,
  "services_offered": ["emergency", "leak", "drain", "sink", "toilet"],
  "license_number": "NY-123456",
  "is_insured": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

### Get Available Leads

```
GET /plumber/api/leads?page=1
```

**Response:**
```json
{
  "leads": [
    {
      "id": "lead-uuid-1",
      "city": "New York",
      "state": "NY",
      "service_needed": ["leak", "sink"],
      "urgency": "today",
      "created_at": "2025-03-01T14:30:00Z",
      "distance_miles": 5.2
    },
    {
      "id": "lead-uuid-2",
      "city": "Brooklyn",
      "state": "NY",
      "service_needed": ["toilet"],
      "urgency": "tomorrow",
      "created_at": "2025-03-01T15:45:00Z",
      "distance_miles": 8.7
    }
  ],
  "page": 1,
  "has_more": true,
  "lead_credits": 10
}
```

### Get Lead Details

```
GET /plumber/api/leads/{lead_id}
```

**Response:**
```json
{
  "id": "lead-uuid-1",
  "city": "New York",
  "state": "NY",
  "service_needed": ["leak", "sink"],
  "urgency": "today",
  "created_at": "2025-03-01T14:30:00Z",
  "problem_description": "Leaking kitchen sink",
  "distance_miles": 5.2
}
```

### Claim Lead

```
POST /plumber/api/leads/{lead_id}/claim
```

**Request Body:**
```json
{
  "notes": "I can help with this leak today."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Lead claimed successfully",
  "lead_credits_remaining": 9,
  "customer_details": {
    "name": "John Doe",
    "phone": "555-123-4567",
    "email": "customer@example.com",
    "address": "123 Main St, New York, NY 10001"
  }
}
```

### Get Claimed Leads

```
GET /plumber/api/my-leads?status=all&page=1
```

**Response:**
```json
{
  "leads": [
    {
      "id": "lead-uuid-1",
      "customer_name": "John Doe",
      "city": "New York",
      "state": "NY",
      "service_needed": ["leak", "sink"],
      "urgency": "today",
      "claimed_at": "2025-03-01T15:05:22Z",
      "status": "contacted",
      "customer_details": {
        "phone": "555-123-4567",
        "email": "customer@example.com",
        "address": "123 Main St, New York, NY 10001"
      }
    }
  ],
  "page": 1,
  "has_more": false
}
```

### Update Lead Status

```
PUT /plumber/api/my-leads/{claim_id}/status
```

**Request Body:**
```json
{
  "status": "completed",
  "contact_status": "reached",
  "notes": "Fixed the leak and replaced the faucet."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Lead status updated successfully"
}
```

### Get Subscription Status

```
GET /plumber/api/subscription
```

**Response:**
```json
{
  "subscription_status": "active",
  "stripe_subscription_id": "sub_12345",
  "current_period_end": "2025-04-01T00:00:00Z",
  "plan": {
    "name": "Monthly Subscription",
    "price": 49.99,
    "currency": "USD"
  },
  "payment_method": {
    "brand": "visa",
    "last4": "4242",
    "exp_month": 12,
    "exp_year": 2025
  }
}
```

### Create Subscription Checkout

```
POST /plumber/api/subscription/checkout
```

**Response:**
```json
{
  "success": true,
  "checkout_url": "https://checkout.stripe.com/c/pay/..."
}
```

### Purchase Lead Credits

```
POST /plumber/api/leads/purchase
```

**Request Body:**
```json
{
  "credit_count": 10
}
```

**Response:**
```json
{
  "success": true,
  "client_secret": "pi_3Nzd..._secret_89Wd...",
  "amount": 100.00,
  "credit_count": 10
}
```

## Admin Endpoints

### Get All Leads

```
GET /admin/api/leads?status=all&page=1
```

**Response:**
```json
{
  "leads": [
    {
      "id": "lead-uuid-1",
      "customer_name": "John Doe",
      "email": "customer@example.com",
      "city": "New York",
      "state": "NY",
      "service_needed": ["leak", "sink"],
      "status": "claimed",
      "created_at": "2025-03-01T14:30:00Z",
      "claim_count": 1
    }
  ],
  "page": 1,
  "total_pages": 5,
  "total_count": 42
}
```

### Get All Plumbers

```
GET /admin/api/plumbers?subscription=active&page=1
```

**Response:**
```json
{
  "plumbers": [
    {
      "id": "plumber-uuid",
      "company_name": "Ace Plumbing",
      "contact_name": "Mike Smith",
      "email": "mike@aceplumbing.com",
      "city": "New York",
      "state": "NY",
      "subscription_status": "active",
      "lead_credits": 10,
      "created_at": "2025-01-15T10:20:30Z"
    }
  ],
  "page": 1,
  "total_pages": 3,
  "total_count": 25
}
```

### Add Lead Credits

```
POST /admin/api/plumbers/{plumber_id}/add-credits
```

**Request Body:**
```json
{
  "credit_count": 5,
  "notes": "Courtesy credits for service issue"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Added 5 lead credits",
  "new_balance": 15
}
```

### Generate Reports

```
GET /admin/api/reports?type=revenue&start_date=2025-02-01&end_date=2025-03-01
```

**Response:**
```json
{
  "report_type": "revenue",
  "start_date": "2025-02-01",
  "end_date": "2025-03-01",
  "data": {
    "subscription_revenue": 2499.50,
    "lead_credit_revenue": 1250.00,
    "total_revenue": 3749.50,
    "transaction_count": 45
  }
}
```

### Update Platform Settings

```
PUT /admin/api/settings
```

**Request Body:**
```json
{
  "lead_radius": 30,
  "lead_price": 12.50,
  "app_name": "Plumber Leads Pro",
  "subscription_price_id": "price_1NjF..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Settings updated successfully"
}
```

## Webhook Endpoints

### Stripe Webhook

```
POST /webhooks/stripe
```

Processes Stripe webhook events such as:
- `checkout.session.completed`
- `invoice.paid`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `payment_intent.succeeded`

This endpoint requires a valid Stripe signature in the `Stripe-Signature` header.

## Error Responses

All API endpoints use standard HTTP status codes and return error details in a consistent format:

**Example Error Response:**
```json
{
  "success": false,
  "error": "Invalid input data",
  "error_type": "validation_error",
  "details": {
    "email": "Invalid email format",
    "phone": "Phone number is required"
  }
}
```

Common error status codes:
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Not authorized to access the resource
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

---

Last Updated: March 1, 2025

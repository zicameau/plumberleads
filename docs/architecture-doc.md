# System Architecture

This document outlines the architecture of the Plumber Lead Generation Website.

## Overview

The Plumber Lead Generation Website is designed as a multi-tier application that connects customers with plumbers using a lead generation model. The system is built with Python Flask on the backend, Supabase for authentication and database, and Stripe for payment processing.

## Architecture Diagram

```
┌────────────────┐     ┌──────────────────┐     ┌───────────────┐
│                │     │                  │     │               │
│   Customers    │────▶│  Flask Web App   │────▶│    Supabase   │
│                │     │                  │     │  (Auth, DB)   │
└────────────────┘     └──────────────────┘     └───────────────┘
                               │   ▲
                               │   │
                               ▼   │
┌────────────────┐     ┌──────────────────┐     ┌───────────────┐
│                │     │                  │     │               │
│    Plumbers    │────▶│  External APIs   │────▶│     Stripe    │
│                │     │                  │     │  (Payments)   │
└────────────────┘     └──────────────────┘     └───────────────┘
                               │
                               │
                               ▼
                       ┌──────────────────┐
                       │                  │
                       │  Email/SMS       │
                       │  Notifications   │
                       │                  │
                       └──────────────────┘
```

## Core Components

### 1. User Interface

The application provides different interfaces for the following user roles:

- **Customers**: Form for service requests, request tracking
- **Plumbers**: Dashboard for lead management, profile and subscription management
- **Administrators**: Platform management, reporting, settings

### 2. Web Application (Flask)

The Flask application handles HTTP requests, business logic, and renders templates. Key components include:

- **Routes**: Handle HTTP requests and responses
- **Services**: Implement business logic
- **Models**: Define data structures and interact with the database
- **Templates**: Render HTML views

### 3. Database (Supabase PostgreSQL)

Supabase provides a PostgreSQL database with PostGIS extension for geo queries. Key tables:

- **auth.users**: User accounts with roles
- **plumbers**: Plumber profiles and subscription data
- **leads**: Customer service requests
- **lead_claims**: Records of plumbers claiming leads
- **settings**: Platform configuration

### 4. Authentication (Supabase Auth)

Supabase Auth provides:

- User registration and login
- Password management
- Email verification
- Role-based access control
- JWT tokens for API authentication

### 5. Payment Processing (Stripe)

Stripe integration handles:

- Monthly subscriptions for plumbers
- Lead credit purchases
- Payment methods management
- Webhook processing for payment events

### 6. External Services

The application integrates with several external services:

- **Geocoding**: Convert addresses to coordinates for geo-matching
- **Email Service**: Send email notifications via SMTP
- **SMS Service**: Send text notifications via Twilio (optional)

## Data Flow

### Customer Service Request Flow

1. Customer fills out the service request form
2. System geocodes the address to get coordinates
3. Request is stored in the leads table
4. System finds matching plumbers based on location and services
5. Notification sent to matching plumbers
6. Confirmation sent to customer

### Plumber Lead Access Flow

1. Plumber receives notification of a new lead
2. Plumber views lead summary in dashboard
3. Plumber claims lead using a lead credit
4. System records the claim and updates lead status
5. Plumber receives customer contact details
6. Customer is notified their request was claimed

### Subscription Management Flow

1. Plumber registers an account
2. Plumber completes profile with service area and offerings
3. Plumber selects a subscription plan
4. System redirects to Stripe Checkout
5. After successful payment, system activates subscription
6. Plumber can now access leads in their service area

## Security Architecture

### Authentication and Authorization

- JWT-based authentication via Supabase
- Role-based access control (admin, plumber)
- Row-level security in database
- CSRF protection for forms

### Data Protection

- HTTPS for all connections
- Secure storage of credentials and API keys
- Database encryption
- Sensitive data handling according to PCI-DSS

## Deployment Architecture

### Production Environment

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Application  │────▶│    Nginx      │────▶│   Database    │
│    Server     │     │  Web Server   │     │  (Supabase)   │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
       │                                            ▲
       │                                            │
       ▼                                            │
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  Background   │────▶│  Cache Layer  │────▶│   External    │
│    Workers    │     │   (Redis)     │     │    Services   │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

### Docker Containers

The application is containerized for consistent deployment:

- **Web**: Flask application
- **Database**: Supabase (PostgreSQL)
- **Nginx**: Web server and reverse proxy
- **Redis**: Cache (optional)

### Scaling Considerations

- Horizontal scaling of web servers
- Database read replicas for high traffic
- Caching for frequently accessed data
- CDN for static assets

## Technical Decisions

### Framework Selection

- **Flask**: Lightweight, flexible, and well-suited for API development
- **Supabase**: Provides authentication, database, and real-time capabilities without managing separate services
- **Stripe**: Robust payment processing with extensive documentation and libraries

### Database Design

- PostgreSQL with PostGIS extension for geo queries
- Normalized schema for data integrity
- Spatial indexes for efficient location-based queries

### API Architecture

- RESTful API design principles
- JSON response format
- Versioned API endpoints for backward compatibility

## Monitoring and Logging

- Application logs with structured logging
- Error tracking and alerting
- Performance monitoring
- Database query monitoring
- Payment event tracking

## Disaster Recovery

- Regular database backups
- Point-in-time recovery
- Transaction logs
- Geographic redundancy (for production)

---

Last Updated: March 1, 2025

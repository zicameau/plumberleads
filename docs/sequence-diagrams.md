# Sequence Diagrams

This document outlines the key flows in the Plumber Leads Platform using sequence diagrams.

## Plumber Registration Flow

```mermaid
sequenceDiagram
    participant P as Plumber
    participant UI as Web Interface
    participant API as Flask API
    participant Auth as Supabase Auth
    participant DB as Database
    participant S as Stripe

    P->>UI: Fill registration form
    UI->>API: Submit registration data
    API->>Auth: Create user account
    Auth-->>API: Return user token
    API->>S: Create Stripe customer
    S-->>API: Return Stripe customer ID
    API->>DB: Store plumber data
    DB-->>API: Confirm storage
    API-->>UI: Registration success
    UI-->>P: Show dashboard
```

## Lead Assignment Flow

```mermaid
sequenceDiagram
    participant E as External Service
    participant API as Flask API
    participant DB as Database
    participant N as Notification Service
    participant P as Plumber

    E->>API: Submit new lead
    API->>DB: Store lead data
    API->>DB: Query matching plumbers
    DB-->>API: Return matching plumbers
    API->>N: Send notification
    N->>P: Email/SMS notification
    P->>API: Accept lead
    API->>DB: Update lead status
    API->>N: Send confirmation
```

## Payment Processing Flow

```mermaid
sequenceDiagram
    participant P as Plumber
    participant UI as Web Interface
    participant API as Flask API
    participant S as Stripe
    participant DB as Database

    P->>UI: Accept lead
    UI->>API: Confirm lead acceptance
    API->>S: Create payment intent
    S-->>API: Return client secret
    API->>UI: Return payment details
    UI->>S: Complete payment
    S-->>API: Webhook: Payment success
    API->>DB: Update lead status
    API->>P: Send confirmation
```

## Notification Flow

```mermaid
sequenceDiagram
    participant API as Flask API
    participant N as Notification Service
    participant E as Email Service
    participant S as SMS Service
    participant R as Recipient

    API->>N: Send notification request
    N->>N: Process notification type
    alt is email
        N->>E: Send email
        E-->>R: Deliver email
    else is SMS
        N->>S: Send SMS
        S-->>R: Deliver SMS
    end
    N-->>API: Notification status
``` 
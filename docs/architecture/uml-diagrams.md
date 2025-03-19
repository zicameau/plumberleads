# PlumberLeads UML Diagrams

This document contains various UML diagrams representing the architecture and behavior of the PlumberLeads system.

## Class Diagrams

### Core Domain Model

```mermaid
classDiagram
    class User {
        +UUID id
        +String email
        +String passwordHash
        +String name
        +String phone
        +String role
        +DateTime createdAt
        +DateTime updatedAt
        +authenticate()
        +updateProfile()
    }
    
    class Plumber {
        +UUID id
        +String company
        +String profileImage
        +String[] serviceAreas
        +String[] serviceTypes
        +String subscriptionStatus
        +viewLeads()
        +claimLead()
        +updateServiceAreas()
    }
    
    class Admin {
        +manageUsers()
        +manageLeads()
        +viewReports()
        +configureSettings()
    }
    
    class Lead {
        +UUID id
        +String customerName
        +String customerPhone
        +String customerEmail
        +String serviceArea
        +String serviceType
        +String description
        +String address
        +String status
        +Decimal price
        +String source
        +UUID claimedBy
        +DateTime claimedAt
        +DateTime completedAt
        +DateTime createdAt
        +DateTime updatedAt
        +claim()
        +complete()
        +cancel()
    }
    
    class Payment {
        +UUID id
        +UUID plumberId
        +UUID leadId
        +Decimal amount
        +String currency
        +String status
        +String paymentIntentId
        +String paymentMethodId
        +String receiptUrl
        +DateTime createdAt
        +process()
        +refund()
    }
    
    class PaymentMethod {
        +UUID id
        +UUID plumberId
        +String type
        +String details
        +Boolean isDefault
        +DateTime createdAt
        +setDefault()
        +delete()
    }
    
    class Notification {
        +UUID id
        +UUID userId
        +String type
        +String title
        +String message
        +Boolean isRead
        +DateTime createdAt
        +markAsRead()
    }
    
    User <|-- Plumber
    User <|-- Admin
    Plumber "1" -- "many" Lead : claims
    Plumber "1" -- "many" Payment : makes
    Plumber "1" -- "many" PaymentMethod : has
    Lead "1" -- "1" Payment : generates
    User "1" -- "many" Notification : receives
```

## Sequence Diagrams

### Lead Claiming Process

```mermaid
sequenceDiagram
    participant P as Plumber
    participant FE as Frontend
    participant API as API
    participant DB as Database
    participant SS as Stripe Service
    participant NS as Notification Service
    
    P->>FE: Browse available leads
    FE->>API: GET /leads
    API->>DB: Query available leads
    DB-->>API: Return leads
    API-->>FE: Return leads list
    FE-->>P: Display leads
    
    P->>FE: Select lead to claim
    FE->>API: GET /leads/{id}
    API->>DB: Get lead details
    DB-->>API: Return lead details
    API-->>FE: Return lead details
    FE-->>P: Display lead details
    
    P->>FE: Click "Claim Lead"
    FE->>API: POST /leads/{id}/claim
    API->>SS: Create payment intent
    SS-->>API: Return payment intent
    API->>DB: Update lead status to pending
    API-->>FE: Return payment URL
    
    FE->>SS: Redirect to payment
    P->>SS: Submit payment info
    SS->>SS: Process payment
    SS-->>P: Payment confirmation
    SS->>API: Payment webhook
    
    API->>DB: Update lead status to claimed
    API->>DB: Store payment record
    API->>NS: Send notification
    
    NS->>P: Send confirmation email/SMS
    API-->>FE: Redirect to claimed lead
    FE-->>P: Show full lead details
```

### User Registration Process

```mermaid
sequenceDiagram
    participant P as Plumber
    participant FE as Frontend
    participant API as API
    participant Auth as AuthService
    participant DB as Database
    participant Email as EmailService
    
    P->>FE: Fill registration form
    FE->>API: POST /auth/register
    API->>Auth: Validate and create user
    Auth->>DB: Store user details
    DB-->>Auth: Confirm storage
    Auth->>Auth: Generate JWT token
    Auth-->>API: Return user and token
    API->>Email: Send welcome email
    API-->>FE: Return user and token
    FE->>FE: Store token
    FE-->>P: Display success & redirect
```

## State Diagrams

### Lead Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Available : Created
    Available --> PendingPayment : Plumber claims
    PendingPayment --> Claimed : Payment successful
    PendingPayment --> Available : Payment failed
    Available --> Expired : After 48 hours
    Claimed --> Completed : Job finished
    Claimed --> Disputed : Problem reported
    Disputed --> Refunded : Refund approved
    Disputed --> Completed : Dispute resolved
    Completed --> [*]
    Refunded --> [*]
    Expired --> [*]
```

### Plumber Subscription States

```mermaid
stateDiagram-v2
    [*] --> Pending : Registration
    Pending --> Active : Payment method added
    Active --> Past Due : Payment failed
    Past Due --> Active : Payment successful
    Past Due --> Suspended : No payment after 7 days
    Suspended --> Active : Account reactivated
    Suspended --> Cancelled : After 30 days
    Active --> Cancelled : Plumber cancels
    Cancelled --> [*]
```

## Component Diagram

```mermaid
graph TD
    subgraph "Frontend Layer"
    A[Public Website] --> B[Authentication Module]
    B --> C[Plumber Dashboard]
    B --> D[Admin Dashboard]
    end
    
    subgraph "API Layer"
    E[Auth API] --> F[Plumber API]
    E --> G[Admin API]
    F --> H[Leads API]
    F --> I[Payments API]
    G --> H
    G --> I
    end
    
    subgraph "Service Layer"
    H --> J[Lead Service]
    I --> K[Payment Service]
    F --> L[Notification Service]
    G --> L
    end
    
    subgraph "Data Layer"
    J --> M[(Database)]
    K --> M
    L --> M
    end
    
    subgraph "External Services"
    K --> N[Stripe]
    L --> O[Email Service]
    L --> P[SMS Service]
    end
```

## Deployment Diagram

```mermaid
graph TD
    subgraph "Client Side"
    A[Browser] --> B[Mobile Device]
    A[Browser] --> C[Desktop]
    end
    
    subgraph "Frontend Hosting - Vercel"
    B --> D[Next.js Frontend]
    C --> D
    end
    
    subgraph "Backend Services - Vercel"
    D --> E[Next.js API Routes]
    end
    
    subgraph "Database - Supabase"
    E --> F[PostgreSQL]
    E --> G[Auth Services]
    end
    
    subgraph "External Services"
    E --> H[Stripe]
    E --> I[SendGrid]
    E --> J[Twilio]
    end
    
    subgraph "Monitoring & Logging"
    E --> K[Error Tracking]
    D --> K
    K --> L[Notifications]
    end
```

## Use Case Diagram

```mermaid
graph TD
    subgraph "Actors"
    A((Plumber))
    B((Admin))
    C((System))
    end
    
    subgraph "Authentication"
    A --> D[Register Account]
    A --> E[Login]
    A --> F[Reset Password]
    B --> E
    end
    
    subgraph "Lead Management"
    A --> G[Browse Leads]
    A --> H[View Lead Details]
    A --> I[Claim Lead]
    A --> J[Mark Lead Completed]
    B --> K[Create Lead]
    B --> L[Edit Lead]
    B --> M[Delete Lead]
    C --> N[Generate Leads from Ads]
    end
    
    subgraph "Payment Processing"
    A --> O[Pay for Lead]
    A --> P[Add Payment Method]
    A --> Q[View Payment History]
    B --> R[Issue Refund]
    end
    
    subgraph "Profile Management"
    A --> S[Update Profile]
    A --> T[Configure Service Areas]
    A --> U[Update Subscription]
    end
    
    subgraph "Admin Tasks"
    B --> V[Manage Plumbers]
    B --> W[View Reports]
    B --> X[Configure Settings]
    end
```

These diagrams provide a comprehensive visualization of the PlumberLeads system architecture, behavior, and relationships between components. 
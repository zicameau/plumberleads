# PlumberLeads Database Schema

## Overview

The PlumberLeads platform uses PostgreSQL via Supabase for data storage. This document outlines the database schema, including tables, relationships, fields, and indexes.

## Entity Relationship Diagram

```
+----------------+       +---------------+       +----------------+
|    Plumbers    |       |     Leads     |       |    Payments    |
+----------------+       +---------------+       +----------------+
| PK id          |<----->| PK id         |<----->| PK id          |
|    name        |       |    customer_* |       |    amount      |
|    email       |       |    service_*  |       |    stripe_id   |
|    phone       |       |    status     |       |    created_at  |
|    password    |       |    price      |       |    updated_at  |
|    company     |       |    created_at |       | FK plumber_id  |
|    services    |       |    updated_at |       | FK lead_id     |
|    locations   |       | FK plumber_id |       +----------------+
|    created_at  |       +---------------+
|    updated_at  |               ^
+----------------+               |
        ^                        |
        |                        |
        |                +---------------+
        |                |  LeadNotes    |
        |                +---------------+
        |                | PK id         |
        |                |    note       |
        |                |    created_at |
        |                | FK lead_id    |
        |                | FK author_id  |
        |                +---------------+
        |
        |
+----------------+       +---------------+
| ServiceAreas   |       |   Services    |
+----------------+       +---------------+
| PK id          |       | PK id         |
|    zip_code    |       |    name       |
|    city        |       |    description|
|    state       |       |    base_price |
|    created_at  |       |    active     |
| FK plumber_id  |       |    created_at |
+----------------+       +---------------+
```

## Tables

### Users

Stores authentication and profile information for all users in the system.

| Column     | Type         | Constraints       | Description                               |
|------------|--------------|-------------------|-------------------------------------------|
| id         | uuid         | PK, NOT NULL      | Unique identifier for the user            |
| email      | varchar(255) | UNIQUE, NOT NULL  | User's email address                      |
| password   | varchar(255) | NOT NULL          | Hashed password                           |
| user_type  | enum         | NOT NULL          | 'plumber', 'admin'                        |
| created_at | timestamp    | NOT NULL, DEFAULT | Account creation timestamp                |
| updated_at | timestamp    | NOT NULL, DEFAULT | Account last update timestamp             |

Indexes:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)

### Plumbers

Stores detailed information about plumbers.

| Column      | Type         | Constraints       | Description                              |
|-------------|--------------|-------------------|------------------------------------------|
| id          | uuid         | PK, NOT NULL      | Unique identifier (same as users.id)     |
| name        | varchar(255) | NOT NULL          | Plumber's full name                      |
| company     | varchar(255) |                   | Business name                            |
| phone       | varchar(50)  | NOT NULL          | Contact phone number                     |
| website     | varchar(255) |                   | Business website URL                     |
| bio         | text         |                   | Business description                     |
| logo_url    | varchar(255) |                   | URL to logo image                        |
| approved    | boolean      | NOT NULL, DEFAULT | Account approval status                  |
| rating      | decimal(3,2) |                   | Average rating (future feature)          |
| status      | enum         | NOT NULL, DEFAULT | 'active', 'suspended', 'inactive'        |
| created_at  | timestamp    | NOT NULL, DEFAULT | Record creation timestamp                |
| updated_at  | timestamp    | NOT NULL, DEFAULT | Record update timestamp                  |

Indexes:
- PRIMARY KEY (id)
- INDEX (status)
- INDEX (approved)

### ServiceAreas

Defines geographic areas where plumbers provide services.

| Column      | Type         | Constraints       | Description                              |
|-------------|--------------|-------------------|------------------------------------------|
| id          | uuid         | PK, NOT NULL      | Unique identifier                        |
| plumber_id  | uuid         | FK, NOT NULL      | Reference to plumbers.id                 |
| zip_code    | varchar(20)  | NOT NULL          | Service area zip/postal code             |
| city        | varchar(100) | NOT NULL          | City name                                |
| state       | varchar(50)  | NOT NULL          | State/province                           |
| radius      | integer      |                   | Service radius in miles/km (optional)    |
| created_at  | timestamp    | NOT NULL, DEFAULT | Record creation timestamp                |
| updated_at  | timestamp    | NOT NULL, DEFAULT | Record update timestamp                  |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (plumber_id) REFERENCES plumbers(id) ON DELETE CASCADE
- INDEX (zip_code)
- UNIQUE INDEX (plumber_id, zip_code)

### Services

Defines service categories that can be offered by plumbers or requested by customers.

| Column      | Type         | Constraints       | Description                              |
|-------------|--------------|-------------------|------------------------------------------|
| id          | uuid         | PK, NOT NULL      | Unique identifier                        |
| name        | varchar(100) | NOT NULL          | Service name                             |
| description | text         | NOT NULL          | Service description                      |
| base_price  | decimal(10,2)| NOT NULL          | Base price for leads in this category    |
| active      | boolean      | NOT NULL, DEFAULT | Whether service is active                |
| created_at  | timestamp    | NOT NULL, DEFAULT | Record creation timestamp                |
| updated_at  | timestamp    | NOT NULL, DEFAULT | Record update timestamp                  |

Indexes:
- PRIMARY KEY (id)
- UNIQUE INDEX (name)
- INDEX (active)

### PlumberServices

Junction table linking plumbers to the services they offer.

| Column      | Type         | Constraints       | Description                              |
|-------------|--------------|-------------------|------------------------------------------|
| id          | uuid         | PK, NOT NULL      | Unique identifier                        |
| plumber_id  | uuid         | FK, NOT NULL      | Reference to plumbers.id                 |
| service_id  | uuid         | FK, NOT NULL      | Reference to services.id                 |
| created_at  | timestamp    | NOT NULL, DEFAULT | Record creation timestamp                |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (plumber_id) REFERENCES plumbers(id) ON DELETE CASCADE
- FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
- UNIQUE INDEX (plumber_id, service_id)

### Leads

Stores information about customer service requests.

| Column           | Type          | Constraints       | Description                              |
|------------------|---------------|-------------------|------------------------------------------|
| id               | uuid          | PK, NOT NULL      | Unique identifier                        |
| service_id       | uuid          | FK, NOT NULL      | Reference to services.id                 |
| customer_name    | varchar(255)  | NOT NULL          | Customer's name                          |
| customer_email   | varchar(255)  | NOT NULL          | Customer's email address                 |
| customer_phone   | varchar(50)   | NOT NULL          | Customer's phone number                  |
| zip_code         | varchar(20)   | NOT NULL          | Customer's zip/postal code               |
| address          | varchar(255)  |                   | Customer's address (hidden until claimed)|
| service_details  | text          | NOT NULL          | Description of service needed            |
| urgency          | enum          | NOT NULL          | 'low', 'medium', 'high', 'emergency'     |
| price            | decimal(10,2) | NOT NULL          | Price to claim this lead                 |
| status           | enum          | NOT NULL, DEFAULT | 'new', 'claimed', 'completed', 'invalid' |
| plumber_id       | uuid          | FK                | Reference to plumbers.id (if claimed)    |
| source           | varchar(100)  | NOT NULL          | Lead acquisition channel                 |
| created_at       | timestamp     | NOT NULL, DEFAULT | Record creation timestamp                |
| updated_at       | timestamp     | NOT NULL, DEFAULT | Record update timestamp                  |
| claimed_at       | timestamp     |                   | When lead was claimed                    |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (service_id) REFERENCES services(id)
- FOREIGN KEY (plumber_id) REFERENCES plumbers(id) ON DELETE SET NULL
- INDEX (status)
- INDEX (zip_code)
- INDEX (created_at)
- INDEX (source)

### LeadNotes

Stores notes and updates about leads.

| Column      | Type         | Constraints       | Description                              |
|-------------|--------------|-------------------|------------------------------------------|
| id          | uuid         | PK, NOT NULL      | Unique identifier                        |
| lead_id     | uuid         | FK, NOT NULL      | Reference to leads.id                    |
| author_id   | uuid         | FK, NOT NULL      | Reference to users.id                    |
| note        | text         | NOT NULL          | Note content                             |
| created_at  | timestamp    | NOT NULL, DEFAULT | Record creation timestamp                |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
- FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
- INDEX (lead_id)
- INDEX (created_at)

### LeadAttachments

Stores files uploaded by customers related to their service request.

| Column      | Type         | Constraints       | Description                              |
|-------------|--------------|-------------------|------------------------------------------|
| id          | uuid         | PK, NOT NULL      | Unique identifier                        |
| lead_id     | uuid         | FK, NOT NULL      | Reference to leads.id                    |
| file_name   | varchar(255) | NOT NULL          | Original file name                       |
| file_type   | varchar(100) | NOT NULL          | MIME type                                |
| file_size   | integer      | NOT NULL          | File size in bytes                       |
| file_url    | varchar(255) | NOT NULL          | URL to stored file                       |
| created_at  | timestamp    | NOT NULL, DEFAULT | Record creation timestamp                |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
- INDEX (lead_id)

### Payments

Stores payment transactions for lead claims.

| Column      | Type          | Constraints       | Description                              |
|-------------|---------------|-------------------|------------------------------------------|
| id          | uuid          | PK, NOT NULL      | Unique identifier                        |
| plumber_id  | uuid          | FK, NOT NULL      | Reference to plumbers.id                 |
| lead_id     | uuid          | FK, NOT NULL      | Reference to leads.id                    |
| amount      | decimal(10,2) | NOT NULL          | Payment amount                           |
| stripe_id   | varchar(255)  | NOT NULL          | Stripe payment identifier                |
| status      | enum          | NOT NULL          | 'succeeded', 'pending', 'failed'         |
| created_at  | timestamp     | NOT NULL, DEFAULT | Record creation timestamp                |
| updated_at  | timestamp     | NOT NULL, DEFAULT | Record update timestamp                  |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (plumber_id) REFERENCES plumbers(id) ON DELETE RESTRICT
- FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE RESTRICT
- UNIQUE INDEX (lead_id, status) WHERE status = 'succeeded'
- INDEX (stripe_id)
- INDEX (created_at)

### Notifications

Stores notifications sent to users.

| Column      | Type         | Constraints       | Description                              |
|-------------|--------------|-------------------|------------------------------------------|
| id          | uuid         | PK, NOT NULL      | Unique identifier                        |
| user_id     | uuid         | FK, NOT NULL      | Reference to users.id                    |
| type        | enum         | NOT NULL          | 'new_lead', 'lead_claimed', etc.         |
| title       | varchar(255) | NOT NULL          | Notification title                       |
| message     | text         | NOT NULL          | Notification content                     |
| read        | boolean      | NOT NULL, DEFAULT | Whether notification has been read       |
| data        | jsonb        |                   | Additional payload data                  |
| created_at  | timestamp    | NOT NULL, DEFAULT | Record creation timestamp                |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- INDEX (user_id, read)
- INDEX (created_at)

### NotificationSettings

Stores user preferences for notifications.

| Column         | Type         | Constraints       | Description                              |
|----------------|--------------|-------------------|------------------------------------------|
| id             | uuid         | PK, NOT NULL      | Unique identifier                        |
| user_id        | uuid         | FK, NOT NULL      | Reference to users.id                    |
| email_enabled  | boolean      | NOT NULL, DEFAULT | Whether email notifications are enabled  |
| sms_enabled    | boolean      | NOT NULL, DEFAULT | Whether SMS notifications are enabled    |
| push_enabled   | boolean      | NOT NULL, DEFAULT | Whether push notifications are enabled   |
| quiet_start    | time         |                   | Start of quiet hours (no notifications)  |
| quiet_end      | time         |                   | End of quiet hours                       |
| preferences    | jsonb        | NOT NULL, DEFAULT | Detailed notification preferences        |
| updated_at     | timestamp    | NOT NULL, DEFAULT | Record update timestamp                  |

Indexes:
- PRIMARY KEY (id)
- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- UNIQUE INDEX (user_id)

## Data Relationships

1. **Users to Plumbers**: One-to-one relationship. Each plumber account is associated with exactly one user account.

2. **Plumbers to ServiceAreas**: One-to-many relationship. A plumber can serve multiple service areas.

3. **Plumbers to Services**: Many-to-many relationship. Plumbers can offer multiple services, and each service can be offered by multiple plumbers.

4. **Leads to Services**: Many-to-one relationship. Each lead is associated with one service category.

5. **Leads to Plumbers**: Many-to-one relationship. A lead is claimed by at most one plumber, and a plumber can claim many leads.

6. **Leads to LeadNotes**: One-to-many relationship. A lead can have multiple notes.

7. **Leads to LeadAttachments**: One-to-many relationship. A lead can have multiple file attachments.

8. **Leads to Payments**: One-to-many relationship. A lead can have multiple payment attempts, but only one successful payment.

9. **Users to Notifications**: One-to-many relationship. A user can receive multiple notifications.

10. **Users to NotificationSettings**: One-to-one relationship. Each user has one notification settings record.

## Database Constraints and Validations

1. **Uniqueness Constraints**:
   - Email addresses must be unique across all users
   - A plumber cannot claim a lead that is already claimed
   - A plumber cannot have duplicate service areas or services

2. **Referential Integrity**:
   - Cascading deletes for related records where appropriate
   - Restrict deletes for payment records to prevent data loss

3. **Value Constraints**:
   - Service prices must be positive values
   - Lead status transitions must follow a defined workflow
   - Phone numbers must follow a valid format

## Indexing Strategy

1. **Primary Keys**: UUID for all tables for scalability and security

2. **Performance Indexes**:
   - Zip code searches for leads and service areas
   - Status filtering for leads and plumbers
   - Timestamp-based queries for all tables

3. **Foreign Key Indexes**: All foreign key columns are indexed to optimize joins

## Migration Strategy

Database migrations will be handled using Supabase migrations or a dedicated migration tool like Prisma. Each migration will be versioned and include:

1. Schema changes
2. Data transformations
3. Rollback procedures

## Security Considerations

1. **Row-Level Security (RLS)**: Implemented in Supabase to control access to data
   - Plumbers can only see their own profile and leads
   - Admins have access to all records

2. **Data Encryption**:
   - Sensitive customer information is encrypted at rest
   - Payment details are handled by Stripe, not stored directly

3. **Audit Logging**:
   - Changes to critical data are logged with timestamp and user information

## Performance Considerations

1. **Query Optimization**:
   - Specific indexes for common query patterns
   - Denormalization where appropriate for read-heavy operations

2. **Connection Pooling**:
   - Managed by Supabase for optimal database connections

3. **Caching Strategy**:
   - Frequent read-only data can be cached at the application level
   - Cache invalidation triggered by relevant write operations 
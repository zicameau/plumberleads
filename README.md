# Plumber Leads Generation Website

A platform that connects customers with plumbers, using a lead generation model similar to care.com. Customers submit their plumbing service requests, and qualified plumbers in the area are matched to these opportunities.

## Features

- **Customer Lead Generation**: Form for customers to submit plumbing service requests
- **Geo-Based Matching**: Automatically matches service requests to plumbers by location
- **Plumber Dashboard**: Plumbers can view and claim leads in their service area
- **Subscription Model**: Plumbers pay a monthly subscription fee to access the platform
- **Lead Credits**: Pay-per-lead system for plumbers to claim customer details
- **Admin Management**: Complete oversight of the platform, users, and transactions
- **Notification System**: Email and SMS notifications for new leads and updates

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with PostGIS extension for geo queries
- **Authentication**: JWT for local development, Supabase Auth for production
- **Payment Processing**: Stripe
- **Containerization**: Docker
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Email/SMS**: SMTP, Twilio (optional)

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Python](https://www.python.org/downloads/) 3.8 or higher
- [Git](https://git-scm.com/downloads)

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/plumber-leads.git
cd plumber-leads
```

2. **Initialize the database**

```bash
# Run the database initialization script
python init_db.py
```

3. **Start the development environment**

```bash
# Run the application with database initialization
python run.py
```

Or use Docker Compose:

```bash
docker-compose up
```

This will:
- Start PostgreSQL with PostGIS extension
- Create the database schema
- Generate test data
- Start the Flask application
- Start Mailhog for email testing

4. **Access the application**

- Web Application: http://localhost:5000
- Mail Testing: http://localhost:8025

### Environment Setup

The project uses environment variables for configuration. Example files are provided as templates:

1. **Copy the example environment files**

```bash
cp .env.local.example .env.local
cp .env.production.example .env.production
cp .env.test.example .env.test
```

2. **Update the environment variables**

Edit the `.env.local` file with your development credentials:
- Database connection details
- Supabase project URL and API key
- Stripe API keys
- Email and SMS service credentials

**Important**: Never commit your actual `.env.*` files to the repository. They contain sensitive information and are already added to `.gitignore`.

### GitLab Variables Setup

For production deployment, sensitive environment variables should be configured in GitLab:

1. Go to your GitLab project settings
2. Navigate to Settings > CI/CD > Variables
3. Add the following required variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon/public key
   - `SUPABASE_SERVICE_KEY`: Your Supabase service role key (from Project Settings > API > service_role key)
   - `ADMIN_EMAIL`: Admin user email (default: admin@example.com)
   - `ADMIN_PASSWORD`: Admin user password
   - `DB_PASSWORD`: PostgreSQL database password
   - `STRIPE_API_KEY`: Your Stripe secret key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook signing secret
   - `EMAIL_SERVICE_API_KEY`: Your email service API key
   - `SMS_SERVICE_API_KEY`: Your SMS service API key

For each variable:
- Type: Variable
- Environment scope: All (or your specific environment)
- Protect variable: Yes
- Mask variable: Yes (for sensitive values)

**Important**: The `SUPABASE_SERVICE_KEY` is required for proper admin user initialization. This key has elevated privileges and should be kept secure.

### Manual Admin User Setup

Before running the application, you need to manually create the admin user in Supabase:

1. Go to your Supabase project dashboard (https://app.supabase.com)
2. Navigate to Authentication > Users
3. Click "Invite user"
4. Enter the following details:
   - Email: admin@example.com
   - Password: admin123
   - User metadata: `{"role": "admin", "name": "Admin User"}`

This step is required because the automatic admin user creation might fail due to Supabase's security policies or email verification requirements.

### Development Workflow

The project is configured for rapid development with automatic database resets. This approach allows for quick iterations without worrying about migrations during early development.

#### Database Reset

Every time you start the application with `docker-compose up`, the database is automatically reset and populated with test data. This ensures a consistent development environment.

If you want to manually reset the database:

```bash
# Inside the web container
python reset_db.py

# Or from the host
docker-compose exec web python reset_db.py
```

### Test Accounts

After database initialization, the following test accounts are available:

- **Admin**: admin@example.com / admin123
- **Plumbers**: plumber1@example.com, plumber2@example.com, etc. / password123

## Project Structure

```
plumber_leads/
├── app/                    # Application code
│   ├── config/             # Configuration settings
│   ├── models/             # Database models
│   │   └── base.py         # SQLAlchemy model definitions
│   ├── routes/             # Route handlers
│   ├── services/           # Business logic
│   ├── templates/          # Jinja2 templates
│   ├── static/             # Static assets
│   └── utils/              # Utility functions
│       └── fake_data.py    # Fake data generator
├── deployment/             # Deployment configurations
├── docs/                   # Documentation
├── supabase/               # Supabase migrations
│   └── migrations/         # SQL schema definitions
├── reset_db.py             # Database reset script
├── init_db.py              # Database initialization script
├── run.py                  # Application runner with DB initialization
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Production Dockerfile
├── Dockerfile.dev          # Development Dockerfile
└── README.md               # Project documentation
```

## Working with the Database

### Model Approach

The application uses SQLAlchemy models that sync with the Supabase database schema. The models are defined in `app/models/base.py`.

Key models include:
- `User`: Basic user information
- `Plumber`: Plumber profiles with geo data
- `Lead`: Customer service requests
- `LeadClaim`: Records of plumbers claiming leads

### Database Initialization

The `init_db.py` script handles:
1. Creating all database tables if they don't exist
2. Listing all tables that were created
3. Checking if the admin user exists

This approach ensures the database is properly set up before running the application.

### Database Reset

The `reset_db.py` script handles:
1. Dropping all existing tables and types
2. Creating the schema from the SQL file
3. Generating fake data

This approach ensures a clean slate for development without migrations.

## Running Tests

To run the tests with proper database initialization:

```bash
# Run the test script
./run_tests.sh
```

This will:
1. Set up the test environment
2. Initialize the test database
3. Run the tests

## API Documentation

The API documentation is available in the `docs/api-doc.md` file.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Environment Variables Management

### Local Development

For local development, follow the instructions in the [Environment Setup](#environment-setup) section to create your local `.env.*` files based on the example templates.

### GitLab CI/CD Environment Variables

For deployment environments (staging, production), we use GitLab CI/CD Variables to securely store sensitive information:

1. **Access GitLab CI/CD Variables**:
   - Go to your GitLab project
   - Navigate to **Settings > CI/CD > Variables**

2. **Add Variables**:
   - Click on **Add Variable**
   - Enter the variable name (e.g., `DATABASE_URL`)
   - Enter the variable value
   - Configure protection options:
     - **Protect variable**: Limit to protected branches/tags
     - **Mask variable**: Hide value in job logs
   - Click **Add Variable**

3. **Using Variables in CI/CD Pipelines**:
   Variables are automatically available in your CI/CD pipelines and can be referenced in your `.gitlab-ci.yml` file:

   ```yaml
   deploy:
     stage: deploy
     script:
       - echo "Deploying with database URL $DATABASE_URL"
       - # Your deployment commands here
   ```

4. **Using Variables in Deployed Applications**:
   During deployment, you can:
   - Generate environment files from CI/CD variables
   - Pass variables directly to your application
   - Use environment-specific configuration files

For more information, see [GitLab CI/CD Variables Documentation](https://docs.gitlab.com/ci/variables/).
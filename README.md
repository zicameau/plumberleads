# PlumberLeads

PlumberLeads is a platform that connects plumbing professionals with potential customers. Plumbers can claim leads, manage jobs, and grow their business, while customers can quickly find qualified plumbing services.

## Features

- **Lead Management**: Browse and claim new leads in your service area
- **Customer Management**: Keep track of customer information and job details
- **Payment Processing**: Secure payment handling via Stripe
- **User Profiles**: Comprehensive profiles for plumbing professionals
- **Admin Dashboard**: Detailed analytics and management tools
- **API Integration**: RESTful API for mobile and SPA clients

## Tech Stack

- **Backend**: Flask (Python 3.9+)
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Flask-Login with JWT support for API
- **Payment Processing**: Stripe
- **Frontend**: (Separate repository)

## Local Development Setup

### Prerequisites

- Python 3.9+
- PostgreSQL (optional, SQLite can be used for local development)
- Stripe account (for payment processing)
- Supabase account (optional for local development)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourorg/plumberleads.git
   cd plumberleads
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - **Linux/Mac**:
     ```
     source venv/bin/activate
     ```
   - **Windows**:
     ```
     venv\Scripts\activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   
   # Database URL (SQLite for local development)
   DATABASE_URL=sqlite:///plumberleads.db
   
   # Supabase credentials (optional for local dev)
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   
   # Stripe API keys (use test keys for development)
   STRIPE_PUBLIC_KEY=your-stripe-public-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
   
   # Application settings
   LEAD_CLAIM_PERCENTAGE=0.10
   DEFAULT_CURRENCY=USD
   ADMIN_EMAIL=admin@example.com
   
   # Local development mode (set to True to bypass Supabase)
   LOCAL_DEV=True
   ```

6. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

### Running the Application

Start the development server:
```
flask run
```

Or use Python directly:
```
python app.py
```

The application will be available at http://localhost:5000.

### Stripe Webhook Setup (Optional)

For payment processing to work fully in development, you'll need to set up Stripe webhooks:

1. Install the Stripe CLI: https://stripe.com/docs/stripe-cli
2. Forward webhooks to your local server:
   ```
   stripe listen --forward-to http://localhost:5000/api/webhook/stripe
   ```
3. Update your `.env` file with the webhook signing secret provided by the Stripe CLI.

## API Documentation

The API provides endpoints for lead management, user authentication, and payments. The main API routes include:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Leads
- `GET /api/leads` - Get available leads
- `GET /api/leads/<id>` - Get lead details
- `POST /api/leads/<id>/claim` - Claim a lead
- `PUT /api/leads/<id>/status` - Update lead status
- `POST /api/leads/submit` - Submit a new lead (public)

### Plumbers
- `GET /api/plumbers/profile` - Get current plumber profile
- `PUT /api/plumbers/profile` - Update plumber profile
- `GET /api/service-areas` - Get service area options
- `GET /api/service-types` - Get service type options

### Payments
- `GET /api/payments` - Get payment history
- `GET /api/payments/<id>` - Get payment details
- `POST /api/payments/<id>/refund` - Request a refund

### Admin
- `GET /api/admin/stats` - Get dashboard statistics
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/<id>/status` - Update user status
- `GET /api/admin/leads` - Get all leads
- `POST /api/admin/leads` - Create a lead
- `GET /api/admin/logs` - Get system logs
- `GET /api/admin/config` - Get system configuration
- `PUT /api/admin/config` - Update system configuration

## Deployment

For production deployment, follow these steps:

1. Set up a PostgreSQL database
2. Configure environment variables for production
3. Use a WSGI server (Gunicorn, uWSGI) with a reverse proxy (Nginx, Apache)
4. Set up SSL/TLS for secure connections
5. Configure proper logging and monitoring

See the deployment documentation in `docs/deployment/` for detailed instructions.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[MIT License](LICENSE) 
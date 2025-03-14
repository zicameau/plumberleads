# TEST

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
- **Authentication/Database**: Supabase
- **Payment Processing**: Stripe
- **Geo Processing**: PostGIS (via Supabase)
- **Containerization**: Docker
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Email/SMS**: SMTP, Twilio (optional)

## Documentation

For detailed documentation, see the `/docs` directory:

- [Development Guide](docs/development.md) - Local development setup and workflow
- [API Documentation](docs/api.md) - REST API endpoints reference
- [Deployment Guide](docs/deployment.md) - Production deployment instructions
- [System Architecture](docs/architecture.md) - System design and architecture
- [Implementation Checklist](docs/checklist.md) - Project progress tracking

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

2. **Run the setup script**

```bash
chmod +x setup-local.sh
./setup-local.sh
```

3. **Start the development environment**

```bash
docker-compose up
```

4. **Generate test data**

```bash
make fake-data
```

5. **Access the application**

- Web Application: http://localhost:5000
- Supabase Studio: http://localhost:54322
- Mail Testing: http://localhost:8025

## Project Structure

```
plumber_leads/
├── app/                    # Application code
│   ├── config/             # Configuration settings
│   ├── models/             # Database models
│   ├── routes/             # Route handlers
│   ├── services/           # Business logic
│   ├── templates/          # Jinja2 templates
│   ├── static/             # Static assets
│   └── utils/              # Utility functions
├── docs/                   # Documentation
├── tests/                  # Test suite
├── docker/                 # Docker configurations
├── supabase/               # Supabase migrations
└── .vscode/                # VS Code configurations
```

## Development Workflow

The project includes a Makefile with common development tasks:

```bash
# List all available commands
make help

# Start the development environment
make dev

# Run the Flask application locally
make run

# Run tests
make test

# Format code
make format

# Run linters
make lint

# Reset the database (caution: destroys all data)
make db-reset

# Generate fake data for development
make fake-data
```

## Test Accounts

After running `make fake-data`, the following test accounts are available:

- **Admin**: admin@example.com / admin123
- **Plumbers**: plumber1@example.com, plumber2@example.com, etc. / password123

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

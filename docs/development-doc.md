# Development Guide

This guide covers the local development setup and workflow for the Plumber Lead Generation Website.

## Local Development Environment

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git
- Make (optional, but recommended)
- VS Code (recommended, but any editor will work)

### Initial Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/plumber-leads.git
cd plumber-leads
```

2. **Run the setup script**

This will initialize your local development environment:

```bash
chmod +x setup-local.sh
./setup-local.sh
```

The setup script will:
- Create `.env.local` from the example file
- Generate secure random keys for local development
- Create a Python virtual environment and install dependencies
- Set up directories for Supabase data

3. **Review environment variables**

The `.env.local` file contains configuration for your local development environment. Review and update any values as needed:

```bash
# Edit with your preferred editor
nano .env.local
```

Important variables to check:
- MAIL_SERVER, MAIL_PORT, etc. (for email testing)
- STRIPE_TEST_API_KEY (if testing payments)
- TWILIO settings (if testing SMS)

### Starting the Development Environment

Start all services using Docker Compose:

```bash
docker-compose up
```

Or use the Makefile shortcut:

```bash
make dev
```

### Accessing the Services

- **Flask web application**: http://localhost:5000
- **Supabase Studio**: http://localhost:54322
- **Mail testing interface**: http://localhost:8025
- **Node/frontend server** (if enabled): http://localhost:3000

## Development Workflow

### Generating Test Data

Populate the application with test data for development:

```bash
make fake-data
```

This creates:
- Admin user: admin@example.com / admin123
- Plumber users: plumber1@example.com, plumber2@example.com, etc. / password123
- Sample leads and claims in various states

### Common Development Tasks

The Makefile provides shortcuts for common development tasks:

```bash
# List all available commands
make help

# Run the Flask application locally (outside Docker)
make run

# Run the test suite
make test

# Format code with black and isort
make format

# Run linters (flake8, mypy)
make lint

# Reset the database (caution: this deletes all data)
make db-reset

# Run database migrations
make db-migrate
```

### Project Structure

The application follows a modular structure:

- `app/`: Main application code
  - `config/`: Configuration for different environments
  - `models/`: Database models
  - `routes/`: Route handlers
  - `services/`: Business logic
  - `templates/`: Jinja2 templates
  - `static/`: CSS, JS, and images
  - `utils/`: Utility functions

- `tests/`: Test suite
- `docs/`: Documentation
- `supabase/`: Database migrations and volumes

### Using Mock Services

For local development, the application can use mock services to avoid external API dependencies:

- **Mock Email**: Emails are logged to the console and can be viewed in the MailHog UI
- **Mock SMS**: SMS messages are logged to the console
- **Mock Geocoding**: Uses predefined city coordinates with random variations

These can be enabled/disabled in `.env.local`:

```
USE_MOCK_GEOCODING=true
USE_MOCK_EMAIL=true
USE_MOCK_SMS=true
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run a specific test file
pytest tests/test_models.py

# Run tests with coverage report
pytest --cov=app tests/
```

### Writing Tests

Tests use pytest and are organized in the `tests/` directory:

- `conftest.py`: Test fixtures
- `test_models.py`: Tests for database models
- `test_routes.py`: Tests for route handlers
- `test_services.py`: Tests for service functions

Follow these guidelines when writing tests:
- Each test should be independent and self-contained
- Use fixtures for common setup
- Mock external services when appropriate
- Test both success and failure cases

## Debugging

### VS Code Debugging

The project includes VS Code launch configurations for debugging:

1. Open the project in VS Code
2. Go to the Run and Debug panel
3. Select a configuration:
   - `Flask: Run` - Run the application
   - `Flask: Debug` - Run with debugging
   - `Python: Current File` - Debug the current file
   - `Python: Tests` - Debug the test suite

### Debugging in Docker

To debug the application running in Docker:

1. Start the environment with `docker-compose up`
2. In VS Code, use the `Flask: Remote Debug (Docker)` configuration
3. Set breakpoints in your code
4. The debugger will connect to the running container

### Logs

- Application logs are output to the console when running with Docker Compose
- For email testing, check the MailHog interface at http://localhost:8025
- Database logs can be viewed in Supabase Studio at http://localhost:54322

## Frontend Development

### Template Structure

The application uses Jinja2 templates located in `app/templates/`:

- `layout.html`: Base template with common elements
- `customer/`: Customer-facing pages
- `plumber/`: Plumber dashboard pages
- `admin/`: Admin dashboard pages
- `emails/`: Email templates

### CSS Framework

The project uses Tailwind CSS for styling:

- Utility classes are used directly in HTML
- Custom styles can be added in `app/static/css/`

### JavaScript

Add JavaScript files to `app/static/js/` and include them in templates as needed.

## Git Workflow

Follow these guidelines for git:

1. Work on feature branches: `git checkout -b feature/new-feature`
2. Make small, focused commits
3. Update tests for new functionality
4. Run linters before committing: `make lint`
5. Format code before committing: `make format`
6. Create a pull request for review

---
Last Updated: March 1, 2025

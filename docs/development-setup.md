# Development Environment Setup

## Prerequisites

### Required Software
1. **Core Requirements**
   - Python 3.9 or higher
   - Git
   - Docker and Docker Compose
   - PostgreSQL client
   - Node.js 18+ (for frontend development)

2. **Recommended Tools**
   - Visual Studio Code
   - Postman/Insomnia for API testing
   - pgAdmin for database management
   - Python virtual environment manager (virtualenv/venv)

## Initial Setup

### Repository Setup
```bash
# Clone the repository
git clone https://gitlab.com/your-org/plumberleads.git
cd plumberleads

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
1. **Local Environment File**
```bash
# Copy example environment file
cp .env.example .env

# Required environment variables
FLASK_ENV=development
FLASK_DEBUG=1
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
STRIPE_API_KEY=your_stripe_test_key
```

2. **Supabase Database Setup**
   - Create a Supabase project at https://supabase.com
   - Copy your project URL and API keys
   - Run the database migrations using Supabase CLI:
   ```bash
   # Install Supabase CLI
   npm install -g supabase

   # Link to your project
   supabase link --project-ref your-project-ref

   # Apply migrations
   supabase db push
   ```

## Development Tools

### VSCode Configuration
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
}
```

### Recommended Extensions
- Python
- Python Test Explorer
- GitLens
- Docker
- REST Client
- PostgreSQL

## Local Development

### Running the Application
```bash
# Start the development server
flask run

# Start with debugger
flask run --debug

# Start with specific port
flask run --port 5001
```

### Database Management
```bash
# Create new migration
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_leads.py

# Run tests with specific marker
pytest -m "integration"
```

### Test Data
1. **Seeding Development Data**
```bash
# Seed basic test data
flask seed-db

# Reset database to clean state
flask reset-db
```

## Docker Development Environment

### Container Setup
```bash
# Build and start all services
docker-compose up --build

# Start specific service
docker-compose up api

# View logs
docker-compose logs -f
```

### Container Management
```bash
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose up --build api
```

## Debugging

### Debug Configuration
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger"
            ]
        }
    ]
}
```

### Common Issues and Solutions

1. **Database Connection**
   - Verify PostgreSQL is running
   - Check connection string
   - Confirm database exists
   - Verify user permissions

2. **Environment Variables**
   - Ensure .env file exists
   - Verify variable names
   - Check variable values
   - Confirm file permissions

3. **Dependencies**
   - Update requirements.txt
   - Clear pip cache
   - Rebuild virtual environment
   - Check Python version

## Code Style

### Style Guidelines
- Follow PEP 8
- Use Black formatter
- Maximum line length: 88 characters
- Use type hints
- Write docstrings for all functions

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## Git Workflow

### Branch Strategy
1. **Branch Types**
   - main: production code
   - develop: development code
   - feature/*: new features
   - bugfix/*: bug fixes
   - hotfix/*: urgent fixes

2. **Commit Guidelines**
   - Use conventional commits
   - Include ticket numbers
   - Write clear descriptions
   - Keep commits focused

### Code Review Process
1. Create feature branch
2. Write and test code
3. Submit pull request
4. Address review comments
5. Merge after approval 
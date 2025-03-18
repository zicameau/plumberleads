# Plumber Leads Platform Documentation

Welcome to the documentation for the Plumber Leads Platform. This platform connects plumbers with potential customers by managing and distributing leads efficiently.

## Table of Contents

1. [Architecture Overview](architecture.md)
   - System Components
   - Database Schema
   - Environment Variables
   - Security Considerations

2. [Sequence Diagrams](sequence-diagrams.md)
   - Plumber Registration Flow
   - Lead Assignment Flow
   - Payment Processing Flow
   - Notification Flow

3. [User Stories](user-stories.md)
   - Plumber Stories
   - Admin Stories
   - External Service Stories
   - Acceptance Criteria Template

4. [API Documentation](api-endpoints.md)
   - Authentication Endpoints
   - Plumber Endpoints
   - Lead Management Endpoints
   - Admin Endpoints
   - Error Responses

5. [Services Documentation](services.md)
   - Service Categories
   - Service Urgency Levels
   - Pricing Structure
   - Quality Standards
   - Service Area Coverage

6. [Deployment Guide](deployment.md)
   - Prerequisites
   - Environment Setup
   - Deployment Process
   - CI/CD Pipeline
   - Monitoring Setup
   - Backup & Recovery
   - Maintenance Procedures

## Technology Stack

- **Backend Framework**: Python Flask
- **Authentication**: Supabase
- **Database**: Supabase (PostgreSQL)
- **Payment Processing**: Stripe
- **CI/CD**: GitLab
- **Hosting**: Digital Ocean Droplet

## Getting Started

1. Clone the repository
2. Set up environment variables as specified in [Architecture Documentation](architecture.md)
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   flask run
   ```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines for Python code
   - Use type hints
   - Write docstrings for all functions and classes

2. **Testing**
   - Write unit tests for all new features
   - Maintain minimum 80% code coverage
   - Run tests before submitting PR:
     ```bash
     pytest
     ```

3. **Git Workflow**
   - Create feature branches from `develop`
   - Use conventional commits
   - Submit PRs for review
   - Squash merge to `develop`

4. **Security**
   - Never commit sensitive data
   - Use environment variables for secrets
   - Follow OWASP security guidelines
   - Regularly update dependencies

## Project Structure

```
plumberleads/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── __init__.py
│   ├── auth/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── docs/
│   └── (existing documentation)
├── requirements.txt
├── .env.example
├── .gitignore
└── app.py
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please contact the development team at dev@plumberleads.com 
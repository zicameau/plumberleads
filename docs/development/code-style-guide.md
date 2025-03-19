# PlumberLeads Code Style Guide

This document outlines the coding standards and best practices for the PlumberLeads platform. Following these guidelines ensures code consistency, readability, and maintainability across the project.

## Table of Contents

1. [Python Style Guide](#python-style-guide)
2. [HTML Style Guide](#html-style-guide)
3. [CSS Style Guide](#css-style-guide)
4. [JavaScript Style Guide](#javascript-style-guide)
5. [Database Naming Conventions](#database-naming-conventions)
6. [Documentation Guidelines](#documentation-guidelines)
7. [Version Control Practices](#version-control-practices)

## Python Style Guide

The Python code in the PlumberLeads platform follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines with a few project-specific customizations.

### Imports

- Organize imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Separate each import group with a blank line
- Use absolute imports rather than relative imports

```python
# Good
import os
import sys
from datetime import datetime

from flask import Flask, request, render_template
from werkzeug.security import generate_password_hash

from app.models import User
from app.utils.helpers import format_phone_number
```

### Naming Conventions

- **Variables and Functions**: Use `snake_case` for variable and function names
- **Classes**: Use `PascalCase` for class names
- **Constants**: Use `UPPER_CASE` for constants
- **Private Methods/Variables**: Prefix with a single underscore `_`

```python
# Good
MAX_LEADS_PER_PAGE = 20

def calculate_lead_price(service_type, location):
    # Function body

class LeadManager:
    def __init__(self):
        self._active_leads = []
        
    def _validate_lead(self, lead):
        # Private method
```

### Line Length

- Maximum line length is 88 characters (as per Black formatter)
- For long strings or function calls, use parentheses or line continuation

```python
# Good
long_string = (
    "This is a very long string that needs to be "
    "wrapped across multiple lines."
)

result = some_function_with_many_params(
    param1, param2, param3, param4, param5, param6
)
```

### Indentation

- Use 4 spaces for indentation (no tabs)
- For line continuations, align wrapped elements vertically or use a hanging indent of 4 spaces

### Comments

- Use docstrings for all public modules, functions, classes, and methods
- Follow the [Google docstring style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- Use inline comments sparingly and only for complex logic

```python
def claim_lead(lead_id, user_id):
    """Claims a lead for a specific user and processes payment.
    
    Args:
        lead_id: The ID of the lead to claim
        user_id: The ID of the user claiming the lead
        
    Returns:
        dict: The claimed lead information including customer contact details
        
    Raises:
        LeadNotFoundError: If the lead cannot be found
        PaymentError: If the payment processing fails
    """
    # Function body
```

### Flask-Specific Guidelines

- Use blueprints to organize routes by functionality
- Follow RESTful API design practices
- Use Flask-SQLAlchemy models consistently
- Place configuration in a separate module

```python
# app/routes/leads.py
from flask import Blueprint, jsonify, request

leads_bp = Blueprint('leads', __name__, url_prefix='/leads')

@leads_bp.route('/', methods=['GET'])
def get_leads():
    """Returns a list of available leads for the authenticated user."""
    # Implementation
```

## HTML Style Guide

### General Rules

- Use HTML5 doctype: `<!DOCTYPE html>`
- Use lowercase element names and attributes
- Close all HTML elements properly
- Use double quotes for attribute values
- Always specify `alt` attributes for images
- Always specify `lang` attribute in the HTML tag

### Templates

- Use Jinja2 templates for all HTML files
- Modularize templates with includes and extends
- Keep logic in Python, not in templates
- Use consistent indentation (2 spaces)

```html
<!-- Good -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}PlumberLeads{% endblock %}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body>
  {% include 'components/header.html' %}
  
  <main>
    {% block content %}{% endblock %}
  </main>
  
  {% include 'components/footer.html' %}
  
  <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

### Structure

- Use semantic HTML elements (`header`, `nav`, `main`, `section`, `article`, `footer`)
- Avoid div soup; use appropriate HTML5 elements
- Keep nesting to a minimum
- Use appropriate heading hierarchy (h1-h6)

## CSS Style Guide

### Organization

- Organize CSS by component
- Use consistent naming convention (BEM methodology preferred)
- Group related properties together

```css
/* BEM Naming Convention */
.lead-card {
  /* Element styles */
}

.lead-card__title {
  /* Element styles */
}

.lead-card--featured {
  /* Modifier styles */
}
```

### Formatting

- Use a consistent property order (alphabetical or grouped by type)
- Use shorthand properties where appropriate
- Include a space after property name's colon
- End all declarations with a semicolon
- Use a new line for each selector and declaration
- Use lowercase and hyphens for class names

```css
/* Good */
.lead-card {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  font-family: 'Open Sans', sans-serif;
  margin: 0 0 20px;
  padding: 16px;
}
```

### Media Queries

- Use mobile-first approach
- Place media queries near their relevant components
- Use standard breakpoints across the application

```css
.lead-list {
  display: block;
}

@media (min-width: 768px) {
  .lead-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

@media (min-width: 1024px) {
  .lead-list {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## JavaScript Style Guide

### Coding Style

- Use ES6+ features where appropriate
- Use semicolons at the end of statements
- Use single quotes for strings
- Prefer arrow functions for anonymous functions
- Use `const` for values that won't change, `let` otherwise

```javascript
// Good
const MAX_LEADS = 50;
const fetchLeads = async () => {
  const response = await fetch('/api/leads');
  if (!response.ok) {
    throw new Error('Failed to fetch leads');
  }
  return response.json();
};
```

### Event Handling

- Use event delegation where appropriate
- Remove event listeners when they're no longer needed
- Prefer named functions for event handlers

```javascript
// Good
function handleLeadClick(event) {
  const leadId = event.currentTarget.dataset.leadId;
  showLeadDetails(leadId);
}

document.querySelector('.lead-list').addEventListener('click', handleLeadClick);
```

### AJAX Requests

- Use the Fetch API for AJAX requests
- Handle errors appropriately
- Use async/await for cleaner asynchronous code

## Database Naming Conventions

### Tables

- Use plural, snake_case names for tables (e.g., `users`, `service_areas`)
- Use singular names for join tables with both table names (e.g., `user_notification`)

### Columns

- Use snake_case for column names
- Use descriptive names that indicate the purpose of the column
- Prefix boolean columns with `is_`, `has_`, or similar
- Foreign keys should be named as `{table_singular}_id`

```sql
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    service_area_id INTEGER REFERENCES service_areas(id),
    price DECIMAL(10, 2) NOT NULL,
    is_claimed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Documentation Guidelines

### Code Documentation

- Document all functions, classes, and modules with docstrings
- Explain "why" in comments, not just "what"
- Keep documentation up to date when code changes
- Include examples for complex functions

### Project Documentation

- Keep a comprehensive README.md in the root directory
- Document setup, installation, and configuration steps
- Include requirements and dependencies
- Document API endpoints in a separate file

## Version Control Practices

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- First line is a concise summary (50 chars or less)
- Optionally followed by a blank line and detailed explanation
- Reference issue numbers when relevant

```
Add lead filtering by service area

- Implement backend filter query
- Add UI elements to filter form
- Update tests for new functionality

Closes #42
```

### Branching Strategy

- `main` branch should always be deployable
- Use feature branches for new development
- Use the format `feature/short-description`, `bugfix/issue-description`, or `hotfix/urgent-issue`
- Merge through pull requests with at least one review

## Tooling

### Code Formatting and Linting

The following tools are used to enforce code style:

- Python: Black for formatting, Flake8 for linting
- JavaScript: ESLint with Prettier
- HTML/CSS: Prettier

### Pre-commit Hooks

Use the provided pre-commit hooks to ensure code quality before committing:

```bash
pip install pre-commit
pre-commit install
```

## Testing Guidelines

- Write tests for all new features and bug fixes
- Aim for high test coverage, especially on critical paths
- Group tests by functionality
- Use descriptive test method names

```python
def test_lead_claim_updates_status_to_claimed():
    # Test implementation
    
def test_lead_claim_fails_when_already_claimed():
    # Test implementation
```

## Final Notes

This style guide is a living document and may be updated as our best practices evolve. When in doubt about a style issue not covered here, follow the conventions already used in the codebase or consult with the team. 
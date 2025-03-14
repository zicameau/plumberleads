#!/bin/bash
# Script to initialize the database and run tests

# Set environment variables for testing
export FLASK_ENV=testing
export SQLALCHEMY_DATABASE_URI="sqlite:///test.db"

# Initialize the database
echo "Initializing test database..."
python3 init_db.py

# Run the tests
echo "Running tests..."
python3 -m pytest

# Return the exit code from pytest
exit $? 
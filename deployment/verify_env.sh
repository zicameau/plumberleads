#!/bin/bash
# Script to verify environment variables

# Exit on error
set -e

echo "=== Verifying Environment Variables ==="

# Check for required variables
REQUIRED_VARS=(
  "DATABASE_URL"
  "SQLALCHEMY_DATABASE_URI"
  "SUPABASE_URL"
  "SUPABASE_KEY"
  "SECRET_KEY"
  "FLASK_ENV"
  "FLASK_APP"
)

# Path to environment file
ENV_FILE="/opt/plumberleads/.env.production"

# Check if file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: Environment file $ENV_FILE not found!"
  exit 1
fi

# Check each required variable
MISSING_VARS=0
for VAR in "${REQUIRED_VARS[@]}"; do
  if ! grep -q "^$VAR=" "$ENV_FILE"; then
    echo "ERROR: Required variable $VAR is missing from $ENV_FILE"
    MISSING_VARS=$((MISSING_VARS+1))
  else
    echo "✓ $VAR is present"
  fi
done

# Report results
if [ $MISSING_VARS -gt 0 ]; then
  echo "=== VERIFICATION FAILED: $MISSING_VARS required variables are missing ==="
  exit 1
else
  echo "=== VERIFICATION PASSED: All required variables are present ==="
fi

# Test database connection (only if we're not in a CI environment)
if [ -z "$CI" ]; then
  echo "=== Testing Database Connection ==="
  if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
    DB_URL=$(grep "^DATABASE_URL=" "$ENV_FILE" | cut -d '=' -f2-)
    echo "Attempting to connect to database..."
    if command -v pg_isready > /dev/null; then
      # Extract host and port from DATABASE_URL
      DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
      DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
      if [ -z "$DB_PORT" ]; then
        DB_PORT=5432
      fi
      
      pg_isready -h $DB_HOST -p $DB_PORT && echo "✓ Database connection successful" || echo "✗ Database connection failed"
    else
      echo "pg_isready not available, skipping database connection test"
    fi
  fi
fi

echo "=== Environment Verification Complete ===" 
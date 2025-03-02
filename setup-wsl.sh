#!/bin/bash
# setup-wsl.sh

echo "Setting up WSL development environment..."

# Create PostgreSQL directories
mkdir -p supabase/migrations

# Copy local schema SQL to the correct location
if [ -f "supabase/migrations/20240301000000_local_schema.sql" ]; then
    echo "Local schema file exists"
    # Replace the initial schema with the local schema
    cp supabase/migrations/20240301000000_local_schema.sql supabase/migrations/20240301000000_initial_schema.sql
else
    echo "Creating local schema file"
    # If local_schema.sql doesn't exist, create it from the template
    cp supabase-schema.sql supabase/migrations/20240301000000_local_schema.sql
    cp supabase/migrations/20240301000000_local_schema.sql supabase/migrations/20240301000000_initial_schema.sql
fi

# Create config directory if it doesn't exist
mkdir -p app/config

# Create virtual environment
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Create .env.local file if it doesn't exist
if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local
    
    # Generate a random key
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    
    # Replace the placeholder with the random key
    sed -i "s/local-dev-secret-change-me/$SECRET_KEY/g" .env.local
    
    # Set database URL
    echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres" >> .env.local
fi

echo "Setup complete! Run 'docker-compose down --volumes && docker-compose up' to start the development environment."
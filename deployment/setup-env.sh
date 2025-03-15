#!/bin/bash
# Script to create environment file for deployment

# Exit on error
set -e

# Create .env file with required variables
cat > deploy.env << EOF
# Database Configuration
DATABASE_URL=${DATABASE_URL}
SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI}

# Supabase Configuration
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_KEY=${SUPABASE_KEY}

# Docker Configuration
DB_PASSWORD=${DB_PASSWORD}
CI_REGISTRY_IMAGE=${CI_REGISTRY_IMAGE}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG}

# Application Configuration
LOG_LEVEL=DEBUG
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}

# Add any other required environment variables here
EOF

echo "Environment file created successfully" 
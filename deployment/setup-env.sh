#!/bin/bash
# Script to create environment file for deployment

# Exit on error
set -e

# Copy the base .env.production file
cp .env.production .env.production.temp

# Append sensitive variables from GitLab CI/CD
cat >> .env.production.temp << EOF
# Database Configuration
DATABASE_URL=${DATABASE_URL}
SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI}

# Supabase Configuration
SUPABASE_KEY=${SUPABASE_KEY}

# Admin User Configuration
ADMIN_PASSWORD=${ADMIN_PW}

# Application Configuration
SECRET_KEY=${SECRET_KEY}

# Docker Configuration
DB_PASSWORD=${DB_PASSWORD}
CI_REGISTRY_IMAGE=${CI_REGISTRY_IMAGE}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG}
EOF

# Replace the original file with the merged one
mv .env.production.temp .env.production

echo "Environment file created successfully"
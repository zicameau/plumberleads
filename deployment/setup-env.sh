#!/bin/bash
# Script to create environment file for deployment

# Exit on error
set -e

# Create .env file with required variables
cat > deploy.env << EOF
DB_PASSWORD=${DB_PASSWORD}
CI_REGISTRY_IMAGE=${CI_REGISTRY_IMAGE}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG}
LOG_LEVEL=DEBUG
# Add any other required environment variables here
EOF

echo "Environment file created successfully" 
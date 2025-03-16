#!/bin/bash
# Master deployment script that handles all deployment steps

# Exit on error
set -e

echo "=== Starting deployment process ==="

# Step 1: Create environment file
echo "Creating environment file..."
cp .env.production .env.production.temp
cat >> .env.production.temp << EOF
# Database Configuration
DATABASE_URL=${DATABASE_URL}
SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI}
# Supabase Configuration
SUPABASE_KEY=${SUPABASE_KEY}
# Application Configuration
SECRET_KEY=${SECRET_KEY}
# Docker Configuration
DB_PASSWORD=${DB_PASSWORD}
CI_REGISTRY_IMAGE=${CI_REGISTRY_IMAGE}
DOCKER_IMAGE_TAG=${DOCKER_IMAGE_TAG}
# Admin Configuration
ADMIN_PASSWORD=${ADMIN_PW}
EOF
mv .env.production.temp .env.production
echo "Environment file created successfully"

# Step 2: Check if required variables are set
if [ -z "$SERVER_USER" ] || [ -z "$SERVER_IP" ]; then
  echo "ERROR: SERVER_USER or SERVER_IP not set"
  exit 1
fi

# Step 3: Deploy files to server
echo "Deploying files to server..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p /opt/plumberleads/traefik/dynamic"
scp .env.production $SERVER_USER@$SERVER_IP:/opt/plumberleads/.env.production
scp .env.production $SERVER_USER@$SERVER_IP:/opt/plumberleads/.env
scp deployment/docker-compose.yml $SERVER_USER@$SERVER_IP:/opt/plumberleads/docker-compose.yml
scp deployment/traefik/traefik.yml $SERVER_USER@$SERVER_IP:/opt/plumberleads/traefik/traefik.yml
scp deployment/traefik/dynamic/services.yml $SERVER_USER@$SERVER_IP:/opt/plumberleads/traefik/dynamic/services.yml
scp deployment/deploy.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/deploy.sh
scp deployment/debug.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/debug.sh
scp deployment/check_flask_app.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/check_flask_app.sh
scp deployment/logging_config.py $SERVER_USER@$SERVER_IP:/opt/plumberleads/logging_config.py
scp deployment/debug_container.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/debug_container.sh
scp deployment/verify_env.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/verify_env.sh

# Step 4: Run deployment on server
echo "Running deployment on server..."
ssh $SERVER_USER@$SERVER_IP "export CI_REGISTRY=${CI_REGISTRY} && export CI_REGISTRY_USER=${CI_REGISTRY_USER} && export CI_REGISTRY_PASSWORD=${CI_REGISTRY_PASSWORD} && chmod +x /opt/plumberleads/*.sh && /opt/plumberleads/deploy.sh"

echo "=== Deployment completed successfully ===" 
#!/bin/bash
# Script to deploy files to the server

# Exit on error
set -e

# Check if required variables are set
if [ -z "$SERVER_USER" ] || [ -z "$SERVER_IP" ]; then
  echo "ERROR: SERVER_USER or SERVER_IP not set"
  exit 1
fi

# Create directories and copy files
echo "Creating directories and copying files..."
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

# Run deployment
echo "Running deployment..."
ssh $SERVER_USER@$SERVER_IP "export CI_REGISTRY=${CI_REGISTRY} && export CI_REGISTRY_USER=${CI_REGISTRY_USER} && export CI_REGISTRY_PASSWORD=${CI_REGISTRY_PASSWORD} && chmod +x /opt/plumberleads/*.sh && /opt/plumberleads/deploy.sh"

echo "Deployment completed" 
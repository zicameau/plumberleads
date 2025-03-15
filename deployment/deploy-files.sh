#!/bin/bash
# Script to deploy files to the server

# Exit on error
set -e

# Check if required variables are set
if [ -z "$SERVER_USER" ] || [ -z "$SERVER_IP" ]; then
  echo "ERROR: SERVER_USER or SERVER_IP not set"
  exit 1
fi

echo "Creating directories on server..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p /opt/plumberleads/traefik/dynamic"

echo "Copying environment files..."
scp .env.production $SERVER_USER@$SERVER_IP:/opt/plumberleads/.env.production
scp .env.production $SERVER_USER@$SERVER_IP:/opt/plumberleads/.env

echo "Copying configuration files..."
scp deployment/docker-compose.yml $SERVER_USER@$SERVER_IP:/opt/plumberleads/docker-compose.yml
scp deployment/traefik/traefik.yml $SERVER_USER@$SERVER_IP:/opt/plumberleads/traefik/traefik.yml
scp deployment/traefik/dynamic/services.yml $SERVER_USER@$SERVER_IP:/opt/plumberleads/traefik/dynamic/services.yml

echo "Copying scripts..."
scp deployment/deploy.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/deploy.sh
scp deployment/debug.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/debug.sh
scp deployment/check_flask_app.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/check_flask_app.sh
scp deployment/logging_config.py $SERVER_USER@$SERVER_IP:/opt/plumberleads/logging_config.py
scp deployment/debug_container.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/debug_container.sh
scp deployment/verify_env.sh $SERVER_USER@$SERVER_IP:/opt/plumberleads/verify_env.sh

echo "Running deployment script on server..."
ssh $SERVER_USER@$SERVER_IP "export CI_REGISTRY=${CI_REGISTRY} && \
export CI_REGISTRY_USER=${CI_REGISTRY_USER} && \
export CI_REGISTRY_PASSWORD=${CI_REGISTRY_PASSWORD} && \
chmod +x /opt/plumberleads/deploy.sh && \
chmod +x /opt/plumberleads/debug.sh && \
chmod +x /opt/plumberleads/check_flask_app.sh && \
chmod +x /opt/plumberleads/debug_container.sh && \
/opt/plumberleads/deploy.sh"

echo "Creating debug container..."
ssh $SERVER_USER@$SERVER_IP "/opt/plumberleads/debug_container.sh"

echo "Running debug script to collect initial diagnostics..."
ssh $SERVER_USER@$SERVER_IP "/opt/plumberleads/debug.sh"

echo "Testing application access..."
ssh $SERVER_USER@$SERVER_IP "docker exec debug-container curl -v http://web:5000/ || echo 'Failed to access application'"

echo "Deployment completed" 
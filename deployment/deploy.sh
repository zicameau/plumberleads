#!/bin/bash
# Deployment script for Plumber Leads application

# Exit on error
set -e

# Create deployment directories
mkdir -p /opt/plumberleads/traefik/dynamic /opt/plumberleads/logs/traefik /opt/plumberleads/logs/web

# Create and set permissions for acme.json if it doesn't exist
touch /opt/plumberleads/traefik/acme.json
chmod 600 /opt/plumberleads/traefik/acme.json

# Log in to GitLab Container Registry
# Fix: Ensure both username and password are provided correctly
if [ -z "${CI_REGISTRY_USER}" ] || [ -z "${CI_REGISTRY_PASSWORD}" ]; then
  echo "Error: CI_REGISTRY_USER or CI_REGISTRY_PASSWORD environment variables are not set"
  exit 1
fi

# The correct way to use docker login with password-stdin
echo "${CI_REGISTRY_PASSWORD}" | docker login "${CI_REGISTRY}" --username "${CI_REGISTRY_USER}" --password-stdin

# Pull and restart the containers
cd /opt/plumberleads
docker-compose pull
docker-compose up -d --force-recreate

# Copy debugging and logging tools
mkdir -p /opt/plumberleads/tools
cp /opt/plumberleads/debug.sh /opt/plumberleads/tools/
cp /opt/plumberleads/check_flask_app.sh /opt/plumberleads/tools/
chmod +x /opt/plumberleads/tools/*.sh

# Copy logging configuration to the container
docker-compose exec -T web mkdir -p /app/config
docker cp /opt/plumberleads/logging_config.py plumberleads-web-1:/app/config/logging_config.py || echo "Failed to copy logging config"

# Run the Flask application checker
echo "Running Flask application checker..."
docker-compose exec -T web bash /app/check_flask_app.sh > /opt/plumberleads/flask_app_check.log 2>&1 || echo "Failed to run Flask app checker"

# Print logs
echo "Recent application logs:"
docker-compose logs --tail=50 web

# Add firewall configuration
if command -v ufw > /dev/null; then
  echo "Configuring firewall..."
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw allow 8080/tcp
  
  # Enable the firewall if it's not already enabled
  if ! ufw status | grep -q "Status: active"; then
    echo "y" | ufw enable
  fi
  
  echo "Firewall status:"
  ufw status
fi

echo "Deployment completed successfully!"
echo "To debug the application, run: /opt/plumberleads/tools/debug.sh"
echo "To access the application, navigate to: http://SERVER_IP"
echo "To access the Traefik dashboard, navigate to: http://SERVER_IP:8080/dashboard/" 
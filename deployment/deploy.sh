#!/bin/bash
# Deployment script for Plumber Leads application

# Exit on error
set -e

# Create deployment directories
mkdir -p /opt/plumberleads/traefik /opt/plumberleads/logs

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

# Print logs
echo "Recent application logs:"
docker-compose logs --tail=50 web

echo "Deployment completed successfully!" 
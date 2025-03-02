#!/bin/bash
# Script to check Flask application structure

# This script is designed to be run from the debug container
if [ ! -f /.dockerenv ]; then
  echo "This script should be run inside the debug container."
  echo "Run: docker exec -it debug-container bash"
  echo "Then: /opt/plumberleads/check_flask_app.sh"
  exit 1
fi

echo "Checking Flask application structure..."
find /app -type f -name '*.py' 2>/dev/null || echo "Cannot access /app directory"

echo -e "\nChecking web container status..."
curl -v http://web:5000/ 2>&1 || echo "Cannot connect to web container"

echo -e "\nChecking traefik routes..."
curl -v http://traefik:8080/api/http/routers 2>&1 || echo "Cannot connect to traefik API"

echo -e "\nChecking network connectivity..."
ping -c 3 web || echo "Cannot ping web container"
ping -c 3 traefik || echo "Cannot ping traefik container"
ping -c 3 postgres || echo "Cannot ping postgres container"

echo -e "\nChecking DNS resolution..."
nslookup web || echo "Cannot resolve web container"
nslookup traefik || echo "Cannot resolve traefik container"
nslookup postgres || echo "Cannot resolve postgres container"

echo -e "\nChecking port connectivity..."
nc -zv web 5000 || echo "Cannot connect to web:5000"
nc -zv traefik 80 || echo "Cannot connect to traefik:80"
nc -zv traefik 443 || echo "Cannot connect to traefik:443"
nc -zv postgres 5432 || echo "Cannot connect to postgres:5432"

echo -e "\nChecking environment variables..."
env | grep -v PASSWORD | grep -v SECRET | grep -v KEY

echo -e "\nChecking installed Python packages..."
pip list 
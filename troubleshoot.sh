#!/bin/bash
# Troubleshooting script for Bad Gateway error

echo "=== Checking Docker Containers ==="
cd /opt/plumberleads
docker-compose ps

echo -e "\n=== Checking Environment Files ==="
ls -la /opt/plumberleads/.env*

echo -e "\n=== Checking Docker Compose Configuration ==="
grep -A 5 "env_file" /opt/plumberleads/docker-compose.yml

echo -e "\n=== Checking Web Container Logs ==="
docker-compose logs --tail=50 web

echo -e "\n=== Checking Traefik Logs ==="
docker-compose logs --tail=50 traefik

echo -e "\n=== Checking Network Configuration ==="
docker network ls
docker network inspect plumberleads_network

echo -e "\n=== Testing Internal Application Access ==="
docker run --rm --network plumberleads_network alpine sh -c "apk add --no-cache curl && curl -v http://web:5000/" 
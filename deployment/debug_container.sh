#!/bin/bash
# Script to create a temporary debugging container

# Remove existing debug container if it exists
docker rm -f debug-container 2>/dev/null || true

# Create a debugging container
docker run -d --name debug-container \
  --network plumberleads_network \
  -v /opt/plumberleads:/opt/plumberleads \
  ubuntu:20.04 \
  sleep infinity

# Install debugging tools
docker exec debug-container apt-get update
docker exec debug-container apt-get install -y curl iputils-ping net-tools procps python3

echo "Debug container created. You can use it with:"
echo "docker exec -it debug-container bash"
echo "To test the web application, run:"
echo "docker exec debug-container curl -v http://web:5000/" 
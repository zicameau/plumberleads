#!/bin/bash
# Debugging script for Plumber Leads application

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Plumber Leads Debugging Tool${NC}"
echo -e "${YELLOW}Collecting diagnostic information...${NC}"

# Create a directory for debug logs
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEBUG_DIR="/opt/plumberleads/debug_logs_${TIMESTAMP}"
mkdir -p $DEBUG_DIR

# Check if containers are running
echo -e "${YELLOW}Checking container status...${NC}"
docker-compose ps > $DEBUG_DIR/container_status.log
echo "Container status saved to $DEBUG_DIR/container_status.log"

# Check container logs
echo -e "${YELLOW}Collecting container logs...${NC}"
docker-compose logs --tail=500 web > $DEBUG_DIR/web_logs.log
docker-compose logs --tail=200 postgres > $DEBUG_DIR/postgres_logs.log
docker-compose logs --tail=200 traefik > $DEBUG_DIR/traefik_logs.log
echo "Container logs saved to $DEBUG_DIR/"

# Check Traefik routes
echo -e "${YELLOW}Checking Traefik routes...${NC}"
docker-compose exec traefik traefik healthcheck > $DEBUG_DIR/traefik_health.log 2>&1 || echo "Traefik healthcheck not available"

# Check network connectivity
echo -e "${YELLOW}Checking network connectivity...${NC}"
docker network ls > $DEBUG_DIR/network_list.log
docker network inspect plumberleads_network > $DEBUG_DIR/network_info.log 2>&1 || echo "Network not found"

# Check application routes inside the container
echo -e "${YELLOW}Checking application routes...${NC}"
docker-compose exec web bash -c "ls -la /app" > $DEBUG_DIR/app_files.log 2>&1
docker-compose exec web bash -c "find /app -name '*.py' | sort" > $DEBUG_DIR/python_files.log 2>&1
docker-compose exec web bash -c "env" > $DEBUG_DIR/container_env.log 2>&1

# Check if the application is accessible from inside the container
echo -e "${YELLOW}Testing application access...${NC}"
docker-compose exec web curl -v http://localhost:5000/ > $DEBUG_DIR/local_curl.log 2>&1 || echo "Application not accessible locally"

# Check Traefik configuration
echo -e "${YELLOW}Checking Traefik configuration...${NC}"
cat /opt/plumberleads/traefik/traefik.yml > $DEBUG_DIR/traefik_config.log 2>&1

# Check Docker Compose configuration
echo -e "${YELLOW}Checking Docker Compose configuration...${NC}"
cat /opt/plumberleads/docker-compose.yml > $DEBUG_DIR/docker_compose_config.log 2>&1

# Check environment file
echo -e "${YELLOW}Checking environment file...${NC}"
cat /opt/plumberleads/.env | grep -v PASSWORD | grep -v SECRET | grep -v KEY > $DEBUG_DIR/env_file.log 2>&1

# Create a summary file
echo -e "${YELLOW}Creating summary report...${NC}"
cat > $DEBUG_DIR/summary.txt << EOF
Plumber Leads Debug Report
Generated: $(date)

System Information:
------------------
$(uname -a)

Docker Information:
------------------
$(docker info | grep -E 'Server Version|Storage Driver|Logging Driver|Cgroup Driver')

Container Status:
----------------
$(docker-compose ps)

Traefik Routes:
-------------
$(cat $DEBUG_DIR/traefik_health.log 2>/dev/null || echo "No Traefik health information available")

Application Files:
----------------
$(cat $DEBUG_DIR/app_files.log 2>/dev/null || echo "Could not list application files")

Potential Issues:
---------------
$(grep -i "error\|exception\|fail\|warn" $DEBUG_DIR/web_logs.log | tail -20 2>/dev/null)
EOF

echo -e "${GREEN}Debug information collected in $DEBUG_DIR directory${NC}"
echo -e "${YELLOW}To view the summary report, run:${NC}"
echo -e "  ${GREEN}cat $DEBUG_DIR/summary.txt${NC}"
echo -e "${YELLOW}To view detailed web logs, run:${NC}"
echo -e "  ${GREEN}cat $DEBUG_DIR/web_logs.log${NC}" 
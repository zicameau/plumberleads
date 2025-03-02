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
DEBUG_DIR="debug_logs_${TIMESTAMP}"
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
curl -s http://localhost:8080/api/http/routers > $DEBUG_DIR/traefik_routers.log 2>&1 || echo "Traefik API not available"

# Check network connectivity
echo -e "${YELLOW}Checking network connectivity...${NC}"
docker network inspect plumberleads_network > $DEBUG_DIR/network_info.log 2>&1

# Check application routes
echo -e "${YELLOW}Checking application routes...${NC}"
docker-compose exec web python -c "
import sys
try:
    from app import app
    print('Available routes:')
    for rule in app.url_map.iter_rules():
        print(f'{rule.endpoint}: {rule.methods} {rule}')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
" > $DEBUG_DIR/app_routes.log 2>&1 || echo "Could not inspect application routes"

# Check environment variables (redacted)
echo -e "${YELLOW}Checking environment variables...${NC}"
docker-compose exec web env | grep -v PASSWORD | grep -v KEY | grep -v SECRET > $DEBUG_DIR/env_vars.log 2>&1

# Check disk space
echo -e "${YELLOW}Checking disk space...${NC}"
df -h > $DEBUG_DIR/disk_space.log

# Check memory usage
echo -e "${YELLOW}Checking memory usage...${NC}"
free -m > $DEBUG_DIR/memory_usage.log

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
$(docker-compose ps --services | xargs -I{} sh -c "echo {} status: \$(docker-compose ps {} | grep {} | awk '{print \$4,\$5,\$6,\$7}')")

Web Routes Check:
---------------
$(grep "Available routes" $DEBUG_DIR/app_routes.log -A 100 2>/dev/null || echo "Could not retrieve routes")

Potential Issues:
---------------
$(grep -i "error\|exception\|fail\|warn" $DEBUG_DIR/web_logs.log | tail -20 2>/dev/null)
EOF

echo -e "${GREEN}Debug information collected in $DEBUG_DIR directory${NC}"
echo -e "${YELLOW}To view the summary report, run:${NC}"
echo -e "  ${GREEN}cat $DEBUG_DIR/summary.txt${NC}"
echo -e "${YELLOW}To view detailed web logs, run:${NC}"
echo -e "  ${GREEN}cat $DEBUG_DIR/web_logs.log${NC}" 
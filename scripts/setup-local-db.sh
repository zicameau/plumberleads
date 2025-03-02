#!/bin/bash
# Script to set up the local database schema

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up local database schema...${NC}"

# Check if the local_schema.sql file exists
if [ ! -f supabase/migrations/local_schema.sql ]; then
    echo -e "${RED}Error: local_schema.sql not found in supabase/migrations/${NC}"
    exit 1
fi

# Update docker-compose.yml to use local schema
echo -e "${YELLOW}Updating docker-compose.yml to use local schema...${NC}"
sed -i.bak 's|./supabase/migrations:/docker-entrypoint-initdb.d|./supabase/migrations/local_schema.sql:/docker-entrypoint-initdb.d/local_schema.sql|g' docker-compose.yml

echo -e "${GREEN}Local database setup complete!${NC}"
echo -e "${YELLOW}To apply changes, run:${NC}"
echo -e "  ${GREEN}docker-compose down --volumes && docker-compose up${NC}" 
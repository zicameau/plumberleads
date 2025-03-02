#!/bin/bash
# Script to set up the local development environment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up local development environment for Plumber Leads...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker Desktop or Docker Engine.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose.${NC}"
    exit 1
fi

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}Creating .env.local from example...${NC}"
    cp .env.local.example .env.local
    echo -e "${GREEN}Created .env.local - please update with your local configuration.${NC}"
fi

# Create directories for Supabase data persistence
mkdir -p supabase/volumes
mkdir -p supabase/migrations

# Generate random keys for local development
JWT_SECRET=$(openssl rand -hex 32)
ANON_KEY=$(openssl rand -hex 24)
SERVICE_ROLE_KEY=$(openssl rand -hex 24)
SECRET_KEY=$(openssl rand -hex 24)

# Update .env.local with the generated keys
sed -i "" "s/your-super-secret-jwt-token-for-local-dev-only/$JWT_SECRET/g" docker-compose.yml 2>/dev/null || \
sed -i "s/your-super-secret-jwt-token-for-local-dev-only/$JWT_SECRET/g" docker-compose.yml

sed -i "" "s/your-local-anon-key/$ANON_KEY/g" docker-compose.yml 2>/dev/null || \
sed -i "s/your-local-anon-key/$ANON_KEY/g" docker-compose.yml

sed -i "" "s/your-local-service-role-key/$SERVICE_ROLE_KEY/g" docker-compose.yml 2>/dev/null || \
sed -i "s/your-local-service-role-key/$SERVICE_ROLE_KEY/g" docker-compose.yml

sed -i "" "s/local-dev-secret-change-me/$SECRET_KEY/g" .env.local 2>/dev/null || \
sed -i "s/local-dev-secret-change-me/$SECRET_KEY/g" .env.local

# Update Supabase URL and key in .env.local
sed -i "" "s#SUPABASE_URL=.*#SUPABASE_URL=http://localhost:8000#g" .env.local 2>/dev/null || \
sed -i "s#SUPABASE_URL=.*#SUPABASE_URL=http://localhost:8000#g" .env.local

sed -i "" "s/SUPABASE_KEY=.*/SUPABASE_KEY=$ANON_KEY/g" .env.local 2>/dev/null || \
sed -i "s/SUPABASE_KEY=.*/SUPABASE_KEY=$ANON_KEY/g" .env.local

# Update mail settings to use mailhog
sed -i "" "s/MAIL_SERVER=.*/MAIL_SERVER=mailhog/g" .env.local 2>/dev/null || \
sed -i "s/MAIL_SERVER=.*/MAIL_SERVER=mailhog/g" .env.local

sed -i "" "s/MAIL_PORT=.*/MAIL_PORT=1025/g" .env.local 2>/dev/null || \
sed -i "s/MAIL_PORT=.*/MAIL_PORT=1025/g" .env.local

sed -i "" "s/MAIL_USERNAME=.*/MAIL_USERNAME=/g" .env.local 2>/dev/null || \
sed -i "s/MAIL_USERNAME=.*/MAIL_USERNAME=/g" .env.local

sed -i "" "s/MAIL_PASSWORD=.*/MAIL_PASSWORD=/g" .env.local 2>/dev/null || \
sed -i "s/MAIL_PASSWORD=.*/MAIL_PASSWORD=/g" .env.local

# Create venv for local Python development (outside Docker)
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python -m venv venv
source venv/bin/activate || . venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${YELLOW}To start the development environment, run:${NC}"
echo -e "  ${GREEN}docker-compose up${NC}"
echo -e "${YELLOW}Supabase Studio will be available at:${NC}"
echo -e "  ${GREEN}http://localhost:54322${NC}"
echo -e "${YELLOW}API will be available at:${NC}"
echo -e "  ${GREEN}http://localhost:5000${NC}"
echo -e "${YELLOW}Mail testing UI will be available at:${NC}"
echo -e "  ${GREEN}http://localhost:8025${NC}"

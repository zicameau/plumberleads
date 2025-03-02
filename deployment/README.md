# Deployment Instructions

This directory contains the configuration files needed to deploy the Plumber Leads application to a production environment.

## Prerequisites

- A server with Docker and Docker Compose installed
- A domain name pointing to your server
- GitLab CI/CD variables configured for automated deployment

## Manual Deployment

If you need to deploy manually, follow these steps:

1. SSH into your server
2. Create the deployment directory:
   ```bash
   mkdir -p /opt/plumberleads/traefik
   ```
3. Copy the deployment files:
   ```bash
   scp -r deployment/* user@your-server:/opt/plumberleads/
   ```
4. Create and configure the .env file:
   ```bash
   cp .env.production.example /opt/plumberleads/.env
   nano /opt/plumberleads/.env  # Edit with your production values
   ```
5. Create and set permissions for acme.json:
   ```bash
   touch /opt/plumberleads/traefik/acme.json
   chmod 600 /opt/plumberleads/traefik/acme.json
   ```
6. Log in to the GitLab Container Registry:
   ```bash
   docker login registry.gitlab.com
   ```
7. Start the containers:
   ```bash
   cd /opt/plumberleads
   docker-compose pull
   docker-compose up -d
   ```

## Troubleshooting

- Check container logs: `docker-compose logs -f`
- Verify Traefik is running: `docker-compose ps traefik`
- Check SSL certificate status: `docker-compose exec traefik traefik healthcheck` 
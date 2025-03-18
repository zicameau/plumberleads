# Deployment Guide

## Prerequisites

1. **Digital Ocean Account**
   - Account with billing set up
   - API token generated
   - SSH keys configured

2. **Domain Name**
   - Registered domain
   - DNS configured to point to Digital Ocean nameservers

3. **Required Accounts**
   - Supabase account and project created
   - Stripe account with API keys
   - Email service account (e.g., SendGrid)
   - SMS service account (e.g., Twilio)

## Environment Setup

### 1. GitLab CI/CD Variables
```bash
# Authentication
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_KEY=

# Admin Access
ADMIN_EMAIL=
ADMIN_PASSWORD=

# Database
DB_PASSWORD=

# Payment Processing
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=

# Notifications
EMAIL_SERVICE_API_KEY=
SMS_SERVICE_API_KEY=

# Deployment
DO_API_TOKEN=
SSH_PRIVATE_KEY=
```

### 2. Digital Ocean Droplet Setup
```bash
# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y python3-pip nginx certbot python3-certbot-nginx

# Create application user
adduser plumberleads
usermod -aG sudo plumberleads
```

## Deployment Process

### 1. Application Setup
```bash
# Clone repository
git clone https://gitlab.com/your-repo/plumberleads.git
cd plumberleads

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your environment variables
```

### 2. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. SSL Certificate
```bash
# Install SSL certificate
certbot --nginx -d your-domain.com

# Auto-renewal
certbot renew --dry-run
```

### 4. Systemd Service
```ini
[Unit]
Description=Plumber Leads Platform
After=network.target

[Service]
User=plumberleads
WorkingDirectory=/home/plumberleads/app
Environment="PATH=/home/plumberleads/app/venv/bin"
ExecStart=/home/plumberleads/app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

## CI/CD Pipeline

### 1. Testing Stage
```yaml
test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest
  coverage: '/TOTAL.+ ([0-9]{1,3}%)/'
```

### 2. Build Stage
```yaml
build:
  stage: build
  script:
    - docker build -t plumberleads .
    - docker push registry.gitlab.com/your-repo/plumberleads
```

### 3. Deploy Stage
```yaml
deploy:
  stage: deploy
  script:
    - ssh $SERVER_USER@$SERVER_IP "cd /home/plumberleads/app && git pull"
    - ssh $SERVER_USER@$SERVER_IP "sudo systemctl restart plumberleads"
  only:
    - main
```

## Monitoring Setup

### 1. Application Monitoring
- Set up Sentry for error tracking
- Configure logging to file and centralized logging service
- Set up uptime monitoring

### 2. Performance Monitoring
- Configure server metrics collection
- Set up database query monitoring
- Monitor API endpoint performance

### 3. Security Monitoring
- Set up fail2ban for SSH and nginx
- Configure firewall rules
- Monitor for suspicious activities

## Backup Procedures

### 1. Database Backups
```bash
# Automated daily backups
0 0 * * * pg_dump -U postgres plumberleads > /backups/plumberleads_$(date +%Y%m%d).sql

# Backup rotation (keep last 30 days)
find /backups/ -name "plumberleads_*.sql" -mtime +30 -delete
```

### 2. Application Backups
- Regular snapshots of Digital Ocean droplet
- Backup of environment configurations
- Backup of SSL certificates

## Recovery Procedures

### 1. Database Recovery
```bash
# Restore from backup
psql -U postgres plumberleads < /backups/plumberleads_20240318.sql
```

### 2. Application Recovery
- Restore droplet from snapshot
- Redeploy application from GitLab
- Verify system functionality

## Maintenance Procedures

### 1. Regular Updates
```bash
# System updates
apt-get update
apt-get upgrade -y

# Application updates
pip install --upgrade -r requirements.txt
```

### 2. SSL Certificate Renewal
```bash
# Manual renewal
certbot renew
```

### 3. Log Rotation
```bash
# Configure logrotate
/var/log/plumberleads/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 plumberleads plumberleads
} 
# PlumberLeads Deployment Guide

This guide outlines the deployment process for the PlumberLeads platform, detailing the steps required to set up and maintain the production environment.

## Technology Stack Overview

PlumberLeads is deployed on the following technology stack:

- **Frontend**: HTML, CSS, JavaScript
- **Backend API**: Python Flask
- **Database**: PostgreSQL (self-hosted on Digital Ocean)
- **Authentication**: Flask-Login
- **Payments**: Stripe
- **Email**: SendGrid
- **SMS**: Twilio

## Prerequisites

Before deploying, ensure you have:

1. A Digital Ocean account with billing set up
2. SSH access and key pairs generated
3. Access to all required third-party service accounts:
   - Stripe (Production and Test accounts)
   - SendGrid
   - Twilio
4. Git repository access
5. Domain name (registered and with DNS access)
6. SSL certificates (Let's Encrypt)
7. Environment variables document (securely shared)

## Deployment Process

### 1. Server Provisioning (Digital Ocean)

1. **Create a new Droplet in Digital Ocean**
   - Log in to [Digital Ocean](https://cloud.digitalocean.com/)
   - Create a new Droplet with the following specifications:
     - Ubuntu 22.04 LTS
     - Recommended size: Standard Droplet with 2GB RAM, 1 vCPU
     - Enable backups
     - Add your SSH key for secure access
   - Create and attach a volume for database storage (recommended 50GB)

2. **Set up basic server security**
   - Update packages: `sudo apt update && sudo apt upgrade -y`
   - Configure firewall (UFW):
     ```bash
     sudo ufw allow OpenSSH
     sudo ufw allow 80/tcp
     sudo ufw allow 443/tcp
     sudo ufw enable
     ```
   - Create a non-root user with sudo privileges
   - Disable root SSH login

### 2. Database Setup (PostgreSQL)

1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql postgresql-contrib -y
   ```

2. **Configure PostgreSQL**
   - Switch to postgres user: `sudo -i -u postgres`
   - Create a database: `createdb plumberleads`
   - Create a user: `createuser --interactive --pwprompt plumberleadsuser`
   - Grant privileges:
     ```sql
     psql
     GRANT ALL PRIVILEGES ON DATABASE plumberleads TO plumberleadsuser;
     \q
     ```

3. **Initialize the database schema**
   - Import the schema from SQL file:
     ```bash
     psql -U plumberleadsuser -d plumberleads -a -f /path/to/scripts/db/init-schema.sql
     ```
   - Create initial admin user using SQL insert commands

4. **Configure PostgreSQL for remote connections (if needed)**
   - Edit postgresql.conf: `listen_addresses = '*'`
   - Edit pg_hba.conf to allow specific IP addresses
   - Restart PostgreSQL: `sudo systemctl restart postgresql`

### 3. Application Deployment

1. **Install required system packages**
   ```bash
   sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx -y
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/plumberleads.git /var/www/plumberleads
   cd /var/www/plumberleads
   ```

3. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Configure environment variables**
   - Create a .env file in the project directory:
     ```
     # Database
     DATABASE_URL=postgresql://plumberleadsuser:password@localhost:5432/plumberleads
     
     # Flask
     FLASK_APP=app.py
     FLASK_ENV=production
     SECRET_KEY=your_secure_random_secret_key
     
     # Stripe
     STRIPE_PUBLISHABLE_KEY=pk_live_...
     STRIPE_SECRET_KEY=sk_live_...
     STRIPE_WEBHOOK_SECRET=whsec_...
     
     # SendGrid
     SENDGRID_API_KEY=SG....
     EMAIL_FROM=noreply@plumberleads.com
     
     # Twilio
     TWILIO_ACCOUNT_SID=AC...
     TWILIO_AUTH_TOKEN=...
     TWILIO_PHONE_NUMBER=+1...
     ```

5. **Test the application**
   ```bash
   flask run --host=0.0.0.0
   ```

### 4. Setting up Gunicorn and Nginx

1. **Create a systemd service file for Gunicorn**
   ```bash
   sudo nano /etc/systemd/system/plumberleads.service
   ```
   
   Add the following content:
   ```
   [Unit]
   Description=Gunicorn instance to serve PlumberLeads
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/plumberleads
   Environment="PATH=/var/www/plumberleads/venv/bin"
   EnvironmentFile=/var/www/plumberleads/.env
   ExecStart=/var/www/plumberleads/venv/bin/gunicorn --workers 3 --bind unix:plumberleads.sock -m 007 app:app
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Start and enable the Gunicorn service**
   ```bash
   sudo systemctl start plumberleads
   sudo systemctl enable plumberleads
   ```

3. **Configure Nginx as a reverse proxy**
   ```bash
   sudo nano /etc/nginx/sites-available/plumberleads
   ```
   
   Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name plumberleads.com www.plumberleads.com;
   
       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/plumberleads/plumberleads.sock;
       }
   }
   ```

4. **Enable the Nginx site and restart**
   ```bash
   sudo ln -s /etc/nginx/sites-available/plumberleads /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### 5. SSL Configuration with Let's Encrypt

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```

2. **Obtain SSL certificate**
   ```bash
   sudo certbot --nginx -d plumberleads.com -d www.plumberleads.com
   ```

3. **Verify auto-renewal**
   ```bash
   sudo certbot renew --dry-run
   ```

### 6. Third-Party Services Configuration

#### Stripe Setup

1. **Create Stripe products and prices**
   - Set up subscription plans in Stripe dashboard
   - Configure per-lead payment prices
   - Note all product/price IDs for environment variables

2. **Configure Stripe webhooks**
   - Create a webhook endpoint in Stripe Dashboard
   - Point it to: `https://plumberleads.com/webhook/stripe`
   - Select relevant events (payment_intent.succeeded, etc.)
   - Copy webhook signing secret to environment variables

#### SendGrid Setup

1. **Verify sender email**
   - Set up domain authentication in SendGrid
   - Verify email sender
   - Create email templates for:
     - Welcome email
     - Password reset
     - Lead notification
     - Payment receipt

#### Twilio Setup

1. **Configure SMS service**
   - Set up a messaging service in Twilio
   - Configure SMS templates
   - Test SMS sending

## Monitoring and Logging

### Application Monitoring

1. **Set up application logging**
   - Configure Flask logging to write to files
   - Set up log rotation with logrotate

2. **Install and configure Sentry for error tracking**
   ```bash
   pip install sentry-sdk[flask]
   ```
   - Add Sentry initialization to your Flask app
   - Configure error alerts and notifications

3. **Set up Prometheus and Grafana for metrics**
   - Install Prometheus:
     ```bash
     sudo apt install prometheus prometheus-node-exporter -y
     ```
   - Install Grafana:
     ```bash
     sudo apt install apt-transport-https software-properties-common
     sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
     sudo apt update
     sudo apt install grafana
     ```
   - Configure Prometheus to scrape Flask metrics
   - Set up Grafana dashboards for monitoring

### Database Monitoring

1. **PostgreSQL monitoring**
   - Install pg_stat_statements extension
   - Configure PostgreSQL to log slow queries
   - Set up Prometheus PostgreSQL exporter

### Health Checks

1. **Set up health check endpoints**
   - Create `/health` endpoint in Flask app
   - Configure uptime monitoring service (UptimeRobot)

## Backup and Recovery Procedures

### Database Backups

1. **Automated backups using pg_dump**
   - Create a backup script:
     ```bash
     #!/bin/bash
     TIMESTAMP=$(date +"%Y%m%d%H%M%S")
     BACKUP_DIR="/var/backups/postgres"
     
     # Create backup directory if it doesn't exist
     mkdir -p $BACKUP_DIR
     
     # Perform the backup
     pg_dump -U plumberleadsuser -d plumberleads -F c -f $BACKUP_DIR/plumberleads_$TIMESTAMP.dump
     
     # Sync to Digital Ocean Spaces (or other storage)
     s3cmd sync $BACKUP_DIR s3://plumberleads-backups/
     
     # Remove backups older than 30 days
     find $BACKUP_DIR -type f -mtime +30 -name "*.dump" -delete
     ```
   - Make the script executable and add to crontab
     ```bash
     chmod +x /path/to/backup_script.sh
     crontab -e
     # Add: 0 2 * * * /path/to/backup_script.sh
     ```

2. **Backup verification**
   - Regularly verify backup integrity
   - Document backup restoration process

### Disaster Recovery

1. **Recovery procedures**
   - Document step-by-step recovery process
   - Define Recovery Time Objective (RTO) and Recovery Point Objective (RPO)
   - Assign responsible team members

## Security Considerations

### Access Control

1. **Server access**
   - Limit SSH access to specific IP addresses
   - Use SSH keys only, disable password authentication
   - Use sudo for administrative tasks
   - Enable fail2ban to prevent brute force attacks

2. **Secrets management**
   - Use .env files with restricted permissions
   - Consider using a vault solution like HashiCorp Vault
   - Regularly rotate credentials

### Compliance

1. **GDPR considerations**
   - Ensure user data is properly protected
   - Implement data deletion procedures
   - Document data processing activities

2. **PCI compliance**
   - Use Stripe for all payment processing
   - Never store credit card details
   - Follow PCI DSS guidelines

## Scaling Considerations

### Horizontal Scaling

1. **Add multiple Digital Ocean Droplets**
   - Create droplet snapshots for quick scaling
   - Set up Digital Ocean Load Balancer
   - Configure session storage with Redis for shared state

### Database Scaling

1. **PostgreSQL scaling options**
   - Enable connection pooling with PgBouncer
   - Set up read replicas for high-traffic scenarios
   - Consider partitioning large tables

## Rollback Procedures

### Deployment Rollback

1. **Application rollback**
   - Maintain Git tags for releases
   - Create deploy script with version support
   - Document rollback command sequence:
     ```bash
     cd /var/www/plumberleads
     git fetch --all
     git checkout v1.2.3  # previous stable version
     source venv/bin/activate
     pip install -r requirements.txt
     sudo systemctl restart plumberleads
     ```

### Database Rollback

1. **Database restoration process**
   ```bash
   # Stop application
   sudo systemctl stop plumberleads
   
   # Restore from backup
   pg_restore -U plumberleadsuser -d plumberleads -c /path/to/backup_file.dump
   
   # Restart application
   sudo systemctl start plumberleads
   ```

## Maintenance Procedures

### Scheduled Maintenance

1. **Maintenance windows**
   - Define standard maintenance windows
   - Create maintenance mode page in Flask app
   - Communicate maintenance to users in advance

### Version Updates

1. **Dependency updates**
   - Regular security updates
   - Test updates in staging environment
   - Create upgrade plan for major version changes

## Troubleshooting Common Issues

### Deployment Failures

1. **Application not starting**
   - Check Gunicorn and Nginx logs
   - Verify environment variables
   - Check file permissions

### Database Connection Issues

1. **Connection troubleshooting**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in .env file
   - Examine PostgreSQL logs: `/var/log/postgresql/postgresql-*.log`

### Authentication Problems

1. **Auth debugging steps**
   - Check Flask-Login configuration
   - Verify session settings
   - Check database user table

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Security vulnerabilities addressed
- [ ] Environment variables verified
- [ ] Database migrations prepared
- [ ] Third-party services configured

### Deployment
- [ ] Create/update Digital Ocean Droplet
- [ ] Configure server security
- [ ] Deploy application code
- [ ] Set up Gunicorn and Nginx
- [ ] Configure SSL with Let's Encrypt

### Post-Deployment
- [ ] Verify functionality on production
- [ ] Monitor for errors
- [ ] Check third-party integrations
- [ ] Verify email/SMS functionality
- [ ] Test payment processing

## Contact Information

| Role | Name | Contact |
|------|------|---------|
| DevOps Lead | TBD | devops@plumberleads.com |
| Backend Developer | TBD | backend@plumberleads.com |
| Frontend Developer | TBD | frontend@plumberleads.com |
| Emergency Contact | TBD | emergency@plumberleads.com |

## Appendix

### Useful Commands

```bash
# Check Flask application status
sudo systemctl status plumberleads

# View application logs
sudo journalctl -u plumberleads

# Nginx commands
sudo nginx -t  # Test configuration
sudo systemctl restart nginx

# PostgreSQL commands
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -d plumberleads -c "SELECT count(*) FROM users;"

# Backup database
sudo -u postgres pg_dump -d plumberleads -F c -f /path/to/backup.dump
```

### Related Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Digital Ocean Documentation](https://docs.digitalocean.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [SendGrid API Documentation](https://docs.sendgrid.com/api-reference)
- [Twilio API Documentation](https://www.twilio.com/docs/api) 
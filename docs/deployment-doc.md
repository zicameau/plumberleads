# Deployment Guide

This guide covers the deployment process for the Plumber Lead Generation Website to production environments.

## Deployment Options

### Option 1: Docker Deployment

#### Prerequisites

- Linux server with Docker and Docker Compose installed
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)
- Supabase account or self-hosted Supabase
- Stripe account with live API keys

#### Production Docker Setup

1. **Clone the repository on your server**

```bash
git clone https://github.com/yourusername/plumber-leads.git
cd plumber-leads
```

2. **Create production environment file**

```bash
cp .env.example .env
# Edit the .env file with production values
nano .env
```

3. **Set up SSL certificate**

If using Let's Encrypt:

```bash
sudo certbot certonly --standalone -d yourdomain.com
```

4. **Configure Nginx**

Update the Nginx configuration in `docker/nginx/nginx.conf` with your domain and SSL certificate paths.

5. **Build and start the containers**

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

6. **Run database migrations**

```bash
docker-compose -f docker-compose.prod.yml exec web flask db upgrade
```

### Option 2: Cloud Platform Deployment

#### Prerequisites

- Cloud platform account (AWS, GCP, Azure, etc.)
- Familiarity with the chosen cloud platform
- Supabase account
- Stripe account with live API keys

#### AWS Elastic Beanstalk Deployment

1. **Install the AWS CLI and EB CLI**

```bash
pip install awscli awsebcli
```

2. **Configure AWS credentials**

```bash
aws configure
```

3. **Initialize EB application**

```bash
eb init -p python-3.8 plumber-leads
```

4. **Create production environment file**

```bash
cp .env.example .env.prod
# Edit .env.prod with production values
```

5. **Create EB configuration**

Create a file named `.ebextensions/01_environment.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    FLASK_APP: run.py
    FLASK_ENV: production
    # Other environment variables
```

6. **Deploy the application**

```bash
eb create production
```

7. **Configure HTTPS**

In the AWS Console, go to Elastic Beanstalk > Your Environment > Configuration > Load Balancer and add a listener on port 443.

### Option 3: Traditional VPS Deployment

#### Prerequisites

- Linux VPS (Ubuntu 20.04 LTS recommended)
- Nginx or Apache web server
- Python 3.8+
- Supabase account
- Stripe account with live API keys

#### Setup Steps

1. **Update the system**

```bash
sudo apt update
sudo apt upgrade -y
```

2. **Install required packages**

```bash
sudo apt install -y python3-pip python3-venv nginx supervisor
```

3. **Clone the repository**

```bash
git clone https://github.com/yourusername/plumber-leads.git /var/www/plumber-leads
cd /var/www/plumber-leads
```

4. **Set up Python environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

5. **Create production environment file**

```bash
cp .env.example .env
# Edit .env with production values
nano .env
```

6. **Configure Supervisor**

Create `/etc/supervisor/conf.d/plumber-leads.conf`:

```
[program:plumber-leads]
directory=/var/www/plumber-leads
command=/var/www/plumber-leads/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/plumber-leads/gunicorn.err.log
stdout_logfile=/var/log/plumber-leads/gunicorn.out.log
```

7. **Configure Nginx**

Create `/etc/nginx/sites-available/plumber-leads`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. **Enable the site and restart services**

```bash
sudo ln -s /etc/nginx/sites-available/plumber-leads /etc/nginx/sites-enabled/
sudo systemctl restart supervisor
sudo systemctl restart nginx
```

9. **Set up SSL with Let's Encrypt**

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Production Configuration

### Environment Variables

Essential production environment variables include:

```
# Application settings
FLASK_ENV=production
SECRET_KEY=your-secure-random-key
APP_NAME=Plumber Leads

# Supabase settings
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-api-key

# Stripe settings
STRIPE_API_KEY=sk_live_your-stripe-live-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
MONTHLY_SUBSCRIPTION_PRICE_ID=price_your-subscription-price-id

# Email settings
MAIL_SERVER=smtp.yourdomain.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=notifications@yourdomain.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=notifications@yourdomain.com
```

### Security Considerations

1. **Use secure random keys**

Generate a secure random key for your `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

2. **Configure SSL properly**

Ensure all HTTP traffic is redirected to HTTPS.

3. **Set up security headers**

Configure your web server with proper security headers:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://js.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://*.stripe.com;" always;
```

4. **Rotate API keys regularly**

Set up a schedule to rotate sensitive API keys and passwords.

## Database Management

### Backup Strategy

1. **Regular backups**

Set up automated backups for your Supabase database:

```bash
# If using self-hosted Supabase, set up pg_dump to run daily
0 2 * * * pg_dump -U postgres -d plumberleads > /backups/plumberleads-$(date +\%Y\%m\%d).sql
```

2. **Backup rotation**

Keep backups for an appropriate period (e.g., daily for a week, weekly for a month, monthly for a year).

### Migration Process

1. **Create migrations**
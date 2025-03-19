# PlumberLeads Infrastructure Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Infrastructure Architecture Overview](#infrastructure-architecture-overview)
3. [Production Environment](#production-environment)
4. [Development & Testing Environments](#development--testing-environments)
5. [Database Architecture](#database-architecture)
6. [Network Architecture](#network-architecture)
7. [Security Infrastructure](#security-infrastructure)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Disaster Recovery](#disaster-recovery)
10. [Capacity Planning](#capacity-planning)
11. [Infrastructure as Code](#infrastructure-as-code)
12. [Appendices](#appendices)

## Introduction

### Purpose
This document provides a comprehensive overview of the infrastructure supporting the PlumberLeads platform. It details the architecture, configuration, and management of all hardware, software, and network components that make up the production, development, and testing environments.

### Scope
This document covers:
- Server infrastructure
- Database infrastructure
- Network infrastructure
- Security controls
- Monitoring systems
- Backup and recovery procedures
- Development and testing environments

### References
- System Architecture Document
- Deployment Guide
- Security Policies
- Backup & Recovery Procedures

## Infrastructure Architecture Overview

### High-Level Architecture Diagram

```
                                    +-------------------+
                                    |                   |
                                    |  CDN (Cloudflare) |
                                    |                   |
                                    +--------+----------+
                                             |
                                             v
+------------------+              +----------------------+
|                  |              |                      |
|  Load Balancer   +------------->+  Web/App Servers    |
|  (Digital Ocean) |              |  (Digital Ocean)     |
|                  |              |                      |
+------------------+              +----------+-----------+
                                             |
                                             v
                           +----------------------------------+
                           |                                  |
                           |  Database (Supabase PostgreSQL) |
                           |                                  |
                           +----------------+-----------------+
                                            |
              +-------------------------+   |   +------------------------+
              |                         |   |   |                        |
              |  Redis Cache            |<--+-->|  Object Storage       |
              |  (Digital Ocean)        |       |  (Digital Ocean Spaces)|
              |                         |       |                        |
              +-------------------------+       +------------------------+
```

### Component Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| CDN | Cloudflare | Content delivery, DDoS protection |
| Load Balancer | Digital Ocean Load Balancer | Traffic distribution |
| Web/App Servers | Digital Ocean Droplets | Host application code |
| Database | Supabase PostgreSQL | Data storage |
| Cache | Redis | Session store, data caching |
| Object Storage | Digital Ocean Spaces | Store files, images, backups |
| DNS | Cloudflare | Domain name resolution |
| Email Service | SendGrid | Transactional emails |
| SMS Service | Twilio | SMS notifications |
| Payment Processing | Stripe | Handle payments |

## Production Environment

### Server Configuration

#### Web/Application Servers

**Server Type:** Digital Ocean Droplets
**Number of Instances:** 3 (minimum, auto-scaling enabled)
**Instance Size:** Standard Droplet - 4GB RAM, 2 vCPUs
**Region:** NYC1 (Primary), SFO2 (Backup)
**Operating System:** Ubuntu 20.04 LTS
**Web Server:** Nginx 1.18.0
**Application Server:** Gunicorn 20.1.0
**Runtime:** Python 3.9

**Software Components:**
- Flask 2.0.1
- Flask-Login
- Flask-SQLAlchemy
- Flask-Migrate
- Stripe Python Library
- SendGrid Python Library
- Twilio Python Library

**Server Naming Convention:**
- Production: `pl-prod-web-[01-nn]`
- Staging: `pl-stage-web-[01-nn]`

#### Database Service

**Provider:** Supabase
**Service Type:** Managed PostgreSQL
**Plan:** Pro or higher
**Region:** Primary region aligned with application servers
**Database Version:** PostgreSQL 14
**Features Enabled:**
- Point-in-Time Recovery (PITR)
- Daily backups
- Connection pooling
- Database replication

**Security Features:**
- TLS encryption for connections
- Row-Level Security (RLS) policies
- Network restrictions by IP range
- Database auditing

**Integration:**
- Direct PostgreSQL connection for application
- REST API for specific operations
- Real-time subscriptions for live data

#### Cache Servers

**Server Type:** Digital Ocean Managed Redis
**Number of Instances:** 2 (Primary + Replica)
**Instance Size:** 2GB RAM
**Region:** NYC1
**Redis Version:** 6.0
**Eviction Policy:** volatile-lru
**Persistence:** RDB snapshots every 6 hours

### Load Balancer Configuration

**Type:** Digital Ocean Load Balancer
**Algorithm:** Round-robin
**Health Checks:**
- Protocol: HTTPS
- Port: 443
- Path: /health
- Interval: 10 seconds
- Timeout: 5 seconds
- Unhealthy threshold: 3
- Healthy threshold: 5

**SSL Configuration:**
- Certificate: Let's Encrypt wildcard certificate
- SSL Termination: At load balancer
- HTTP to HTTPS redirect: Enabled

### CDN Configuration

**Provider:** Cloudflare
**Plan:** Pro
**Services Used:**
- CDN caching
- DDOS protection
- Web Application Firewall
- DNS management

**Cache Configuration:**
- Browser cache TTL: 4 hours
- Edge cache TTL: 2 hours
- Cache-Control headers: public, max-age=7200

## Development & Testing Environments

### Development Environment

**Server Type:** Digital Ocean Droplet
**Number of Instances:** 1
**Instance Size:** Standard Droplet - 2GB RAM, 1 vCPU
**Region:** NYC1
**Access Method:** SSH with key authentication
**Purpose:** Feature development, code integration

**Database:** Supabase PostgreSQL Development Project

**Key Differences from Production:**
- Reduced resources
- Single instance architecture
- Debug mode enabled
- Test data only
- No auto-scaling

### Staging Environment

**Server Type:** Digital Ocean Droplet
**Number of Instances:** 2
**Instance Size:** Standard Droplet - 4GB RAM, 2 vCPUs
**Region:** NYC1
**Purpose:** Pre-production testing, UAT

**Database:** Supabase PostgreSQL Staging Project

**Key Differences from Production:**
- Isolated from production data
- Production-like architecture
- Connected to test payment gateway
- Anonymized copy of production data

### QA Testing Environment

**Server Type:** Digital Ocean Droplet
**Number of Instances:** 1
**Instance Size:** Standard Droplet - 4GB RAM, 2 vCPUs
**Region:** NYC1
**Purpose:** Automated testing, manual QA

**Database:** Supabase PostgreSQL QA Project

**Key Differences from Production:**
- Isolated environment
- Refreshed daily
- Connected to test services
- Test data only

### Environment Provisioning

All environments are provisioned using Terraform with consistent configurations. Environment-specific variables control the differences between environments.

**Provisioning Process:**
1. Create Terraform configuration
2. Initialize Terraform workspace
3. Apply Terraform plan
4. Deploy application code
5. Run database migrations
6. Verify environment health

## Database Architecture

### Database Structure

**Database Type:** PostgreSQL 14 (via Supabase)
**Hosting:** Supabase Platform
**Primary Database:** `plumberleads_production`
**Schemas:**
- `public` - Main application data
- `auth` - Authentication data (managed by Supabase)
- `reporting` - Reporting views and functions
- `analytics` - Analytics data

### Connection Management

**Connection Pooling:** Built-in Supabase connection pooling
**Min Connections:** 5
**Max Connections:** 50 (adjustable based on plan)
**Connection Timeout:** 30 seconds
**Idle Timeout:** 300 seconds

### Database Access Controls

**Application Access:**
- Read/write access to application schemas
- Connection via password authentication
- Connection string stored in secure environment variables

**Administrative Access:**
- Limited to Database Administrators
- Access via Supabase dashboard with MFA
- Direct SQL access with elevated privileges
- API key rotation policy

### Backup Strategy

**Automated Backups:**
- Daily full backups by Supabase (retained for 7 days)
- Point-in-time recovery enabled (last 7 days)
- Weekly manual exports to external storage

**Backup Storage:**
- Primary: Supabase internal storage
- Secondary: Encrypted backups to AWS S3

**Backup Testing:**
- Monthly restore verification
- Quarterly disaster recovery exercise

### Database Maintenance

**Routine Maintenance:**
- Managed by Supabase
- Automatic vacuuming and optimization
- Scheduled maintenance windows (minimal downtime)
- Automatic minor version updates

**Version Updates:**
- Security patches: Applied automatically by Supabase
- Minor versions: Managed by Supabase
- Major versions: Coordinated with Supabase support

## Network Architecture

### Network Topology

```
                       Internet
                          |
                          v
                +-------------------+
                |                   |
                |  Cloudflare       |
                |  (CDN/WAF)        |
                |                   |
                +--------+----------+
                         |
                         v
             +------------------------+
             |                        |
             |  Digital Ocean         |
             |  Virtual Network       |
             |                        |
             +---+----------------+---+
                 |                |
    +------------v---+    +------v----------+
    |                |    |                 |
    |  Public Subnet |    |  Private Subnet |
    |  (LB, Bastion) |    |  (App Servers)  |
    |                |    |                 |
    +----------------+    +-----------------+
                               |
                               |
                               v
                      +----------------+
                      |                |
                      |  Supabase      |
                      |  PostgreSQL    |
                      |                |
                      +----------------+
```

### Network Segmentation

**Public Subnet:**
- Internet-facing load balancers
- Bastion hosts for administrative access
- Public IP addresses

**Private Subnet:**
- Application servers
- Redis cache
- Internal services
- No direct internet access

### Firewall Rules

**Public Subnet Inbound:**
- HTTP (80): Allow from any (redirected to HTTPS)
- HTTPS (443): Allow from any
- SSH (22): Allow from office IP ranges only

**Private Subnet Inbound:**
- HTTP/HTTPS: Allow from load balancers only
- SSH: Allow from bastion hosts only
- Redis port (6379): Allow from application servers only

**Database Access:**
- Restricted to application server IP addresses
- SSL required for all connections
- Supabase network policies applied

### VPN Configuration

**Provider:** OpenVPN
**Access Control:** LDAP integration
**Two-Factor Authentication:** Enabled (Google Authenticator)
**Client Configurations:** Automated distribution
**Connection Logging:** Enabled

## Security Infrastructure

### Authentication & Authorization

**User Authentication:**
- JWT-based authentication
- Password complexity requirements enforced
- Failed login attempt throttling
- Session timeout: 30 minutes inactive, 12 hours maximum

**Administrative Authentication:**
- Multi-factor authentication required
- IP-based restrictions
- Privileged access management
- Session recording for audit

**Database Authentication:**
- Supabase authentication with secure key management
- API keys rotated regularly
- Service account with minimized privileges
- Connection string secured in environment variables

### Data Encryption

**Data in Transit:**
- TLS 1.3 for all web traffic
- Perfect Forward Secrecy enabled
- Strong cipher suites only
- HSTS implemented
- SSL for database connections

**Data at Rest:**
- Database encryption (provided by Supabase)
- File storage encryption
- Backup encryption

### Security Scanning & Monitoring

**Vulnerability Scanning:**
- Weekly automated scans
- Monthly manual penetration testing
- Dependency scanning in CI/CD pipeline

**Security Monitoring:**
- SIEM integration
- Intrusion detection system
- File integrity monitoring
- Anomaly detection
- Supabase audit logs

### Compliance Controls

**PCI DSS Compliance:**
- Quarterly internal assessments
- Annual external audit
- Segmented cardholder data environment

**GDPR Compliance:**
- Data minimization
- Right to be forgotten implementation
- Data protection impact assessment
- Breach notification procedures

## Monitoring & Alerting

### Monitoring Infrastructure

**Monitoring Solution:** Datadog
**Log Management:** ELK Stack (Elasticsearch, Logstash, Kibana)
**Metrics Collection:**
- System metrics: CPU, memory, disk, network
- Application metrics: Request volume, response time, error rates
- Database metrics: Supabase metrics, query performance, connection count
- Custom business metrics: Lead generation, conversion rates

### Alerting Configuration

**Alerting Channels:**
- Email: For non-urgent notifications
- SMS: For urgent issues
- PagerDuty: For critical incidents
- Slack: For team communication

**Alert Severity Levels:**

| Level | Description | Response Time | Notification Method |
|-------|-------------|---------------|---------------------|
| Critical | Service outage | Immediate | PagerDuty + SMS + Slack |
| High | Major functionality impaired | 15 minutes | PagerDuty + Slack |
| Medium | Performance degradation | 1 hour | Email + Slack |
| Low | Non-impacting issues | Next business day | Email |

**Key Alert Thresholds:**
- CPU usage: >85% for 5 minutes
- Memory usage: >90% for 5 minutes
- Disk usage: >85%
- Response time: >500ms average for 5 minutes
- Error rate: >1% of requests
- Database connection errors: >5 in 5 minutes
- Supabase service status changes

### Dashboards

**Operations Dashboard:**
- System health overview
- Application performance
- Error rates and trends
- Resource utilization
- Supabase health

**Business Dashboard:**
- User registrations
- Lead generation rates
- Conversion metrics
- Revenue tracking

## Disaster Recovery

### Recovery Time Objectives

| Environment | RTO | RPO |
|-------------|-----|-----|
| Production | 1 hour | 5 minutes |
| Staging | 4 hours | 24 hours |
| Development | 24 hours | 24 hours |

### Failover Procedures

**Database Failover:**
- Managed by Supabase (transparent to application)
- Automatic failover to standby nodes
- Application connection resilience with retry logic

**Application Failover:**
1. Health check failure detection
2. Traffic redirection to healthy nodes
3. Automated instance replacement
4. Verification of restored service

**Region Failover:**
1. DNS update to secondary region
2. Application server activation in backup region
3. Database redirection to Supabase backup region (if available)
4. Cache warming procedures

### Backup Restoration

**Database Restoration Procedure:**
1. Identify appropriate restore point in Supabase
2. Initiate point-in-time recovery via Supabase dashboard or API
3. Monitor recovery progress
4. Verify data integrity 
5. Update application connection strings if needed
6. Restart application servers

**Complete System Restoration:**
1. Provision infrastructure using Terraform
2. Restore database using Supabase PITR functionality
3. Deploy application code
4. Restore file storage
5. Update DNS and routing
6. Verify system functionality

### Disaster Recovery Testing

**Scheduled Tests:**
- Monthly: Database restore test using Supabase PITR
- Quarterly: Full DR scenario test
- Annual: Business continuity exercise

**Documentation:**
- DR test results documentation
- Lessons learned analysis
- Procedure updates based on test results

## Capacity Planning

### Current Capacity

**Web/App Tier:**
- Current instances: 3
- Average CPU utilization: 30%
- Average memory utilization: 40%
- Current request capacity: 1,000 req/sec

**Database Tier:**
- Supabase plan: Pro
- Current compute addon: 2x
- Average CPU utilization: 35%
- Average storage utilization: 40% (200GB of 500GB)
- Current concurrent connections: 50

**Cache Tier:**
- Current memory: 2GB
- Average utilization: 30%
- Hit rate: 85%

### Scalability Plans

**Short-term Scaling (0-6 months):**
- Enable auto-scaling for web tier
- Optimize high-traffic queries
- Implement more aggressive caching

**Medium-term Scaling (6-12 months):**
- Upgrade Supabase plan if needed
- Implement database query optimization
- Enhance caching layer

**Long-term Scaling (12+ months):**
- Evaluate microservices architecture
- Consider multi-region active-active setup
- Implement data archival strategy

### Growth Projections

**User Growth Projections:**
- Current: 5,000 active plumbers
- 6 months: 8,000 active plumbers
- 12 months: 15,000 active plumbers

**Infrastructure Impact Analysis:**
- Web tier: Scale to 5 instances at 6 months, 8 at 12 months
- Database: Increase Supabase compute addon at 6 months
- Caching: Increase to 4GB at 6 months, 8GB at 12 months

## Infrastructure as Code

### Terraform Configuration

**Repository Structure:**
- `/terraform/` - Root directory for Terraform configurations
  - `/modules/` - Reusable Terraform modules
  - `/environments/` - Environment-specific configurations
  - `/variables/` - Variable definitions

**Key Modules:**
- `vpc` - Network configuration
- `web` - Web/application servers
- `supabase` - Supabase configuration and access
- `redis` - Caching layer
- `monitoring` - Monitoring infrastructure
- `security` - Security controls

**State Management:**
- Remote state stored in Digital Ocean Spaces
- State locking enabled
- State file encryption

### Deployment Automation

**CI/CD Integration:**
- GitHub Actions for pipeline automation
- Change approval workflow
- Automated testing before deployment
- Rollback capabilities

**Deployment Stages:**
1. Terraform plan generation
2. Plan review and approval
3. Apply infrastructure changes
4. Configuration management
5. Application deployment
6. Health verification

### Configuration Management

**Tool:** Ansible
**Repository:** `/ansible/` in infrastructure repository
**Key Playbooks:**
- `base.yml` - Base server configuration
- `web.yml` - Web server configuration
- `bastion.yml` - Bastion host setup
- `monitoring.yml` - Monitoring agent installation

**Secret Management:**
- Hashicorp Vault for secrets storage
- Encrypted Ansible vault for configuration
- Rotation policy for credentials
- Supabase API keys managed securely

## Appendices

### A. Server Inventory

| Server Name | Environment | Role | IP Address | Specifications |
|-------------|-------------|------|------------|----------------|
| pl-prod-web-01 | Production | Web/App | 10.0.1.10 | 4GB RAM, 2 vCPU |
| pl-prod-web-02 | Production | Web/App | 10.0.1.11 | 4GB RAM, 2 vCPU |
| pl-prod-web-03 | Production | Web/App | 10.0.1.12 | 4GB RAM, 2 vCPU |
| pl-prod-redis-01 | Production | Cache Primary | 10.0.2.20 | 2GB RAM |
| pl-prod-redis-02 | Production | Cache Replica | 10.0.2.21 | 2GB RAM |
| pl-prod-bastion | Production | Bastion Host | 198.51.100.10 | 1GB RAM, 1 vCPU |
| pl-stage-web-01 | Staging | Web/App | 10.1.1.10 | 4GB RAM, 2 vCPU |
| pl-stage-web-02 | Staging | Web/App | 10.1.1.11 | 4GB RAM, 2 vCPU |
| pl-dev-web-01 | Development | Web/App | 10.2.1.10 | 2GB RAM, 1 vCPU |
| pl-qa-web-01 | QA | Web/App | 10.3.1.10 | 4GB RAM, 2 vCPU |

### B. Domain and SSL Configuration

| Domain | Environment | SSL Certificate | Expiration | Renewal Method |
|--------|-------------|----------------|------------|----------------|
| plumberleads.com | Production | Let's Encrypt Wildcard | 2023-12-15 | Automated via Certbot |
| www.plumberleads.com | Production | Let's Encrypt Wildcard | 2023-12-15 | Automated via Certbot |
| api.plumberleads.com | Production | Let's Encrypt Wildcard | 2023-12-15 | Automated via Certbot |
| admin.plumberleads.com | Production | Let's Encrypt Wildcard | 2023-12-15 | Automated via Certbot |
| staging.plumberleads.com | Staging | Let's Encrypt | 2023-12-15 | Automated via Certbot |
| dev.plumberleads.com | Development | Let's Encrypt | 2023-12-15 | Automated via Certbot |

### C. Third-Party Service Configuration

| Service | Purpose | Account Owner | Integration Method |
|---------|---------|--------------|-------------------|
| Supabase | Database & authentication | operations@plumberleads.com | API integration |
| SendGrid | Email delivery | operations@plumberleads.com | API integration |
| Twilio | SMS notifications | operations@plumberleads.com | API integration |
| Stripe | Payment processing | finance@plumberleads.com | API integration |
| Cloudflare | CDN, DNS | operations@plumberleads.com | DNS delegation |
| Datadog | Monitoring | operations@plumberleads.com | Agent installation |
| PagerDuty | Alerting | operations@plumberleads.com | API integration |

### D. Maintenance Procedures

**Routine Maintenance Schedule:**
- Server patching: Monthly (First Sunday, 2:00 AM EST)
- Backup verification: Weekly (Mondays, automated)
- Supabase maintenance: As scheduled by Supabase (typically minimal impact)

**Maintenance Notification Process:**
1. Maintenance calendar updated (2 weeks prior)
2. Email notification to all stakeholders (1 week prior)
3. Reminder notification (24 hours prior)
4. Status page updated during maintenance
5. Completion notification

---

This Infrastructure Documentation will be reviewed and updated quarterly to ensure it reflects current architecture and practices. Last updated: July 2023. 
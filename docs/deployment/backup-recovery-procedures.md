# PlumberLeads Backup & Recovery Procedures

## Table of Contents

1. [Introduction](#introduction)
2. [Backup Strategy](#backup-strategy)
3. [Backup Procedures](#backup-procedures)
4. [Backup Monitoring](#backup-monitoring)
5. [Backup Testing](#backup-testing)
6. [Recovery Scenarios](#recovery-scenarios)
7. [Recovery Procedures](#recovery-procedures)
8. [Disaster Recovery](#disaster-recovery)
9. [Documentation and Reporting](#documentation-and-reporting)
10. [Appendices](#appendices)

## Introduction

### Purpose

This document outlines the backup and recovery procedures for the PlumberLeads platform. It provides detailed instructions for performing routine backups, verifying backup integrity, and executing recovery operations in case of data loss or system failure.

### Scope

This document covers:
- Database backups (Supabase PostgreSQL)
- Application code and configuration
- File storage and uploaded media
- System configuration and infrastructure
- Restoration procedures for various scenarios
- Disaster recovery planning and execution

### References

- System Architecture Document
- Infrastructure Documentation
- Deployment Guide
- Monitoring & Logging Documentation

## Backup Strategy

### Backup Categories

| Category | Components | Criticality | Recovery Point Objective (RPO) | Recovery Time Objective (RTO) |
|----------|------------|-------------|-------------------------------|-------------------------------|
| Database | Supabase PostgreSQL | Critical | 5 minutes | 1 hour |
| Uploaded Media | User profile images, documents | High | 24 hours | 4 hours |
| Application Code | Git repositories, configuration | Medium | 24 hours | 2 hours |
| Infrastructure Configuration | Terraform state, Ansible playbooks | Medium | 24 hours | 8 hours |
| System Configuration | OS settings, nginx configs | Medium | 24 hours | 4 hours |

### Backup Types

#### Full Backups
- Complete database dump
- All uploaded media and static files
- Full system configuration backup
- Complete infrastructure state

#### Incremental Backups
- Database transaction logs (leveraging Supabase features)
- Recently changed files only
- Configuration changes

#### Point-in-Time Recovery
- Supabase PostgreSQL point-in-time recovery (PITR)
- Enables recovery to any point in time within retention period

### Backup Schedule

| Backup Type | Component | Frequency | Retention |
|-------------|-----------|-----------|-----------|
| Full | Database | Daily (1:00 AM UTC) - Supabase automatic | 7 days |
| PITR | Database | Continuous - Supabase feature | 7 days |
| Full | Uploaded Media | Daily (2:00 AM UTC) | 7 days |
| Incremental | Uploaded Media | 6 hours | 24 hours |
| Full | Application Code | After each release | 90 days |
| Full | Infrastructure Config | Weekly | 12 months |
| Full | System Config | Weekly | 90 days |

### Backup Storage

#### Primary Storage
- Supabase (Database backups)
- Digital Ocean Spaces (Primary region: NYC1)
  - Media files
  - Configuration files

#### Secondary Storage
- AWS S3 (Region: us-east-1)
  - Cross-provider redundancy
  - Cold storage for long-term retention
  - Exported database dumps

#### Tertiary Storage (Critical Data Only)
- Offsite physical storage
  - Monthly database full backup
  - Monthly infrastructure configuration

## Backup Procedures

### Database Backup

#### Supabase PostgreSQL Backup

**Automated Backups by Supabase:**
Supabase provides automatic backups as part of their service. These include:
- Daily backups with 7-day retention
- Point-in-time recovery for up to 7 days (Pro plan and above)
- Continuous backup of WAL (Write-Ahead Log) files

**Additional Manual Export Process:**
```bash
# Executed by weekly scheduled job
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/postgresql"
BACKUP_FILE="$BACKUP_DIR/full_backup_$TIMESTAMP.sql.gz"
S3_BUCKET="plumberleads-backups"
S3_PATH="postgresql/full"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Export from Supabase using their CLI
supabase db dump -d plumberleads --file=$BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
  # Upload to secondary storage (AWS S3)
  aws s3 cp $BACKUP_FILE s3://plumberleads-secondary-backups/$S3_PATH/full_backup_$TIMESTAMP.sql.gz

  # Notify monitoring
  curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"success\", \"type\": \"database\", \"backup_file\": \"$BACKUP_FILE\"}" https://monitoring.plumberleads.com/api/backup-notifications

  # Cleanup local file after 24 hours (separate job)
else
  # Notify monitoring of failure
  curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"failed\", \"type\": \"database\", \"error\": \"db dump failed\"}" https://monitoring.plumberleads.com/api/backup-notifications
fi
```

**Manual Export Process:**
1. Access Supabase dashboard
2. Navigate to the Database section
3. Use the "Backup" feature to create a manual backup
4. Download the SQL backup file:
   ```bash
   supabase db dump -d plumberleads | gzip > /tmp/manual_backup_$(date +%Y%m%d_%H%M%S).sql.gz
   ```
5. Transfer backup to secure storage:
   ```bash
   aws s3 cp /tmp/manual_backup_*.sql.gz s3://plumberleads-secondary-backups/postgresql/manual/
   ```
6. Verify backup exists in storage: 
   ```bash
   aws s3 ls s3://plumberleads-secondary-backups/postgresql/manual/
   ```

### File Storage Backup

#### Uploaded Media Backup

**Automated Process:**
```bash
#!/bin/bash
# Executed daily

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MEDIA_DIR="/var/www/plumberleads/media"
BACKUP_DIR="/var/backups/media"
BACKUP_FILE="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"
S3_BUCKET="plumberleads-backups"
S3_PATH="media"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Create tar archive with only files modified in last 24 hours (for incremental)
# For full backup, remove the `-mtime -1` option
find $MEDIA_DIR -type f -mtime -1 | tar -czf $BACKUP_FILE -T -

# Upload to primary storage
s3cmd put $BACKUP_FILE s3://$S3_BUCKET/$S3_PATH/

# Notify monitoring
curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"success\", \"type\": \"media\", \"backup_file\": \"$BACKUP_FILE\"}" https://monitoring.plumberleads.com/api/backup-notifications
```

### Application Code Backup

Application code is primarily stored in Git repositories. After each production deployment, a tag is created and archived.

**Post-Deployment Backup:**
```bash
#!/bin/bash
# Executed after successful deployment

DEPLOYMENT_VERSION="v$(date +%Y.%m.%d)-$(git rev-parse --short HEAD)"
S3_BUCKET="plumberleads-backups"
S3_PATH="application-code"

# Tag the current commit
git tag -a $DEPLOYMENT_VERSION -m "Production deployment $DEPLOYMENT_VERSION"
git push origin $DEPLOYMENT_VERSION

# Create archive of the current code
git archive --format=zip --output=/tmp/$DEPLOYMENT_VERSION.zip $DEPLOYMENT_VERSION

# Upload to primary storage
s3cmd put /tmp/$DEPLOYMENT_VERSION.zip s3://$S3_BUCKET/$S3_PATH/

# Notify monitoring
curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"success\", \"type\": \"application-code\", \"version\": \"$DEPLOYMENT_VERSION\"}" https://monitoring.plumberleads.com/api/backup-notifications
```

### System Configuration Backup

**Automated Process:**
```bash
#!/bin/bash
# Executed weekly

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/system-config"
BACKUP_FILE="$BACKUP_DIR/system_config_$TIMESTAMP.tar.gz"
S3_BUCKET="plumberleads-backups"
S3_PATH="system-config"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Backup key configuration directories
tar -czf $BACKUP_FILE /etc/nginx /etc/systemd/system/plumberleads* /etc/ssl/certs/plumberleads* /etc/environment

# Upload to primary storage
s3cmd put $BACKUP_FILE s3://$S3_BUCKET/$S3_PATH/

# Notify monitoring
curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"success\", \"type\": \"system-config\", \"backup_file\": \"$BACKUP_FILE\"}" https://monitoring.plumberleads.com/api/backup-notifications
```

### Infrastructure Configuration Backup

**Automated Process:**
```bash
#!/bin/bash
# Executed weekly

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/infrastructure"
BACKUP_FILE="$BACKUP_DIR/infrastructure_$TIMESTAMP.tar.gz"
S3_BUCKET="plumberleads-backups"
S3_PATH="infrastructure"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Backup Terraform state and configuration
tar -czf $BACKUP_FILE /path/to/terraform/state /path/to/terraform/config /path/to/ansible/playbooks

# Upload to primary storage
s3cmd put $BACKUP_FILE s3://$S3_BUCKET/$S3_PATH/

# Notify monitoring
curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"success\", \"type\": \"infrastructure\", \"backup_file\": \"$BACKUP_FILE\"}" https://monitoring.plumberleads.com/api/backup-notifications
```

## Backup Monitoring

### Success Verification

All backup processes submit completion status to the monitoring system. The following checks are performed:

1. **Backup Completion Check**
   - Monitor exit status of backup scripts
   - Verify expected backup files exist in storage
   - Check file sizes match expected ranges
   - Verify Supabase automatic backups via API

2. **Backup Integrity Check**
   - For database backups: Perform test restoration to verify integrity
   - For file backups: Verify checksums match expected values
   - For code backups: Verify Git tags and archives exist

### Alerting

**Alert Triggers:**
- Backup process fails to complete
- Backup file size is significantly different from previous backups
- Backup integrity check fails
- Backup storage capacity reaches 80%
- Backup not performed within scheduled window
- Supabase backup status API returns errors

**Alert Recipients:**
- Primary: DevOps Team via PagerDuty
- Secondary: Database Administrator (for database backup failures)
- Tertiary: IT Manager

**Alert Severity:**
- Critical: Database backup failure
- High: Media backup failure
- Medium: Application code backup failure
- Low: System/infrastructure config backup failure

## Backup Testing

### Regular Testing Schedule

| Test Type | Frequency | Components |
|-----------|-----------|------------|
| Database Restore | Weekly | Random database backup |
| File Restore | Monthly | Random selection of media files |
| Full System Restore | Quarterly | Complete restoration to test environment |
| Disaster Recovery | Bi-annually | Complete restoration to DR environment |

### Database Restore Testing

**Automated Test Process:**
```bash
#!/bin/bash
# Executed weekly

# Testing with Supabase restore functionality
TEST_DB_NAME="restore_test_$(date +%Y%m%d)"

# Create a new test database in Supabase (via API)
echo "Creating test database via Supabase API..."
# Use Supabase API to create a test database or schema

# Use point-in-time recovery to restore database (via API)
echo "Restoring database from a random point in time..."
# Use Supabase API to restore to a point in time within last 7 days

# Run validation queries
echo "Running validation queries..."
VALIDATION_RESULT=$(PGPASSWORD=$PG_PASSWORD psql -h $SUPABASE_DB_HOST -U $SUPABASE_DB_USER -d $TEST_DB_NAME -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM leads; SELECT COUNT(*) FROM payments;")

# Report results
curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"completed\", \"type\": \"database-restore-test\", \"validation\": \"$VALIDATION_RESULT\"}" https://monitoring.plumberleads.com/api/backup-notifications

# Cleanup
echo "Cleaning up test database..."
# Use Supabase API to remove test database or schema
```

### Complete System Restore Testing

Quarterly tests involve restoring the entire system to a testing environment:

1. Provision new infrastructure using Terraform
2. Restore system and application configurations
3. Use Supabase database restore functionality for database
4. Restore media files
5. Deploy application code
6. Run a series of automated tests to verify functionality
7. Document any issues encountered
8. Clean up test environment after validation

## Recovery Scenarios

### Scenario 1: Database Corruption

**Impact:** High
**Affected Components:** Database server, potentially application functionality
**Recovery Strategy:** Utilize Supabase point-in-time recovery to restore to a timestamp before corruption

### Scenario 2: Accidental Data Deletion

**Impact:** Medium to High
**Affected Components:** Specific data tables or records
**Recovery Strategy:** Use Supabase point-in-time recovery to restore to the moment before deletion

### Scenario 3: Application Code Issues

**Impact:** Medium
**Affected Components:** Application functionality
**Recovery Strategy:** Rollback to previous code version

### Scenario 4: Server Failure

**Impact:** High
**Affected Components:** Application, potentially connectivity to database
**Recovery Strategy:** Provision new server, restore configurations and deploy application code

### Scenario 5: Complete Infrastructure Loss

**Impact:** Critical
**Affected Components:** All system components except Supabase database
**Recovery Strategy:** Full disaster recovery process, provision new infrastructure on secondary provider if necessary

### Scenario 6: Security Breach

**Impact:** Critical
**Affected Components:** Potentially all systems
**Recovery Strategy:** Provision clean infrastructure, use Supabase point-in-time recovery to restore database to a clean state, apply security patches

## Recovery Procedures

### Database Recovery

#### Supabase Point-in-Time Recovery

**Process via Supabase Dashboard:**
1. Log in to Supabase Dashboard
2. Navigate to Database section
3. Select "Backups" or "Point-in-Time Recovery"
4. Choose the desired recovery point timestamp
5. Initiate the recovery
6. Monitor the recovery progress
7. Verify database state after recovery

**Process via Supabase API:**
```bash
#!/bin/bash
# Execute this script to perform a database restore via Supabase API

# Parameters
RECOVERY_TIMESTAMP=$1  # Timestamp to recover to (format: YYYY-MM-DD HH:MM:SS UTC)
SUPABASE_PROJECT_ID=$2 # Your Supabase project ID
SUPABASE_API_KEY=$3    # Supabase service role key

# Trigger PITR via API
echo "Initiating point-in-time recovery to $RECOVERY_TIMESTAMP..."
curl -X POST "https://api.supabase.io/v1/projects/$SUPABASE_PROJECT_ID/database/pitr" \
  -H "Authorization: Bearer $SUPABASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"recovery_point\": \"$RECOVERY_TIMESTAMP\"}"

# Monitor recovery status
echo "Monitoring recovery status..."
while true; do
  STATUS=$(curl -s "https://api.supabase.io/v1/projects/$SUPABASE_PROJECT_ID/database/pitr/status" \
    -H "Authorization: Bearer $SUPABASE_API_KEY" | jq -r '.status')
  
  echo "Current status: $STATUS"
  if [[ "$STATUS" == "completed" ]]; then
    break
  elif [[ "$STATUS" == "failed" ]]; then
    echo "Recovery failed!"
    exit 1
  fi
  
  sleep 30
done

echo "Recovery to $RECOVERY_TIMESTAMP completed successfully."
```

#### Full Database Recovery (using exported dumps)

**Process:**
```bash
#!/bin/bash
# Execute this script to import a database dump to Supabase

# Parameters
BACKUP_FILE=$1   # S3 path to backup file
SUPABASE_DB_HOST=$2  # Database host
SUPABASE_DB_USER=$3  # Database user
SUPABASE_DB_PASSWORD=$4  # Database password
SUPABASE_DB_NAME=$5  # Database name

# Download backup file
echo "Downloading backup file: $BACKUP_FILE"
aws s3 cp $BACKUP_FILE /tmp/database_restore.sql.gz

# Restore database
echo "Restoring database from backup..."
gunzip -c /tmp/database_restore.sql.gz | PGPASSWORD=$SUPABASE_DB_PASSWORD psql -h $SUPABASE_DB_HOST -U $SUPABASE_DB_USER -d $SUPABASE_DB_NAME

# Verify restore
echo "Verifying database restore..."
TABLE_COUNT=$(PGPASSWORD=$SUPABASE_DB_PASSWORD psql -h $SUPABASE_DB_HOST -U $SUPABASE_DB_USER -d $SUPABASE_DB_NAME -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
USER_COUNT=$(PGPASSWORD=$SUPABASE_DB_PASSWORD psql -h $SUPABASE_DB_HOST -U $SUPABASE_DB_USER -d $SUPABASE_DB_NAME -tAc "SELECT COUNT(*) FROM users;")

echo "Database restore completed with $TABLE_COUNT tables and $USER_COUNT users."

# Cleanup
rm /tmp/database_restore.sql.gz
```

### Media File Recovery

**Process:**
```bash
#!/bin/bash
# Execute this script to restore media files

# Parameters
BACKUP_FILE=$1   # S3 path to backup file
TARGET_DIR=$2    # Directory to restore to

# Download backup file
echo "Downloading media backup file: $BACKUP_FILE"
s3cmd get $BACKUP_FILE /tmp/media_restore.tar.gz

# Create target directory if it doesn't exist
mkdir -p $TARGET_DIR

# Restore files
echo "Restoring media files to $TARGET_DIR..."
tar -xzf /tmp/media_restore.tar.gz -C $TARGET_DIR

# Verify restore
FILE_COUNT=$(find $TARGET_DIR -type f | wc -l)
echo "Media restore completed with $FILE_COUNT files."

# Cleanup
rm /tmp/media_restore.tar.gz

# Fix permissions
chown -R www-data:www-data $TARGET_DIR
```

### Application Code Recovery

**Process:**
```bash
#!/bin/bash
# Execute this script to restore application code to a specific version

# Parameters
VERSION_TAG=$1    # Git tag to restore to
APP_DIR=$2        # Application directory

# Navigate to application directory
cd $APP_DIR

# Backup current state (optional)
git tag -a rollback_$(date +%Y%m%d_%H%M%S) -m "Pre-recovery state"

# Fetch all tags
git fetch --tags

# Checkout specific version
git checkout $VERSION_TAG

# Install dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Restart application
systemctl restart plumberleads-web
systemctl restart plumberleads-worker

# Verify application
echo "Application restored to version $VERSION_TAG. Verify functionality at https://plumberleads.com"
```

### System Configuration Recovery

**Process:**
```bash
#!/bin/bash
# Execute this script to restore system configuration

# Parameters
BACKUP_FILE=$1   # S3 path to backup file

# Download backup file
echo "Downloading system config backup: $BACKUP_FILE"
s3cmd get $BACKUP_FILE /tmp/system_config_restore.tar.gz

# Create backup of current configuration
echo "Backing up current configuration..."
tar -czf /tmp/pre_restore_config_$(date +%Y%m%d_%H%M%S).tar.gz /etc/nginx /etc/systemd/system/plumberleads*

# Restore configuration
echo "Restoring system configuration..."
tar -xzf /tmp/system_config_restore.tar.gz -C /

# Reload services
echo "Reloading services..."
systemctl daemon-reload
systemctl reload nginx

# Cleanup
rm /tmp/system_config_restore.tar.gz

echo "System configuration restored. Verify service status."
```

## Disaster Recovery

### Disaster Recovery Plan

#### Preparation Phase

1. **Documentation**
   - Maintain up-to-date inventory of all systems
   - Document all recovery procedures
   - Maintain contact list for all team members and vendors
   - Document Supabase access credentials and API keys

2. **Recovery Environment**
   - Maintain standby recovery environment with minimal resources
   - Regularly sync Terraform configuration
   - Test recovery procedures bi-annually

3. **Communication Plan**
   - Define communication channels during disaster
   - Establish roles and responsibilities
   - Define escalation path and decision authorities

#### Execution Phase

1. **Assessment**
   - Determine scope of disaster
   - Assess impact on business operations
   - Declare disaster level (partial/complete)
   - Activate disaster recovery team

2. **Communication**
   - Notify stakeholders according to communication plan
   - Provide initial status report
   - Establish regular update schedule

3. **Infrastructure Recovery**
   - Provision recovery infrastructure
   - Restore network configurations
   - Configure security settings

4. **Data Recovery**
   - Use Supabase point-in-time recovery for database
   - Restore file storage
   - Verify data integrity

5. **Application Recovery**
   - Deploy application code
   - Configure application settings
   - Restore integrations with external services

6. **Verification**
   - Run functional tests
   - Verify system performance
   - Validate data consistency

7. **Switchover**
   - Update DNS to point to recovery environment
   - Verify client connections
   - Monitor for issues

### Disaster Recovery Team

| Role | Responsibilities | Primary Contact | Secondary Contact |
|------|------------------|-----------------|-------------------|
| DR Coordinator | Overall coordination, decision-making | CTO | IT Manager |
| Infrastructure Lead | Infrastructure restoration | DevOps Lead | Sr. System Admin |
| Database Lead | Database recovery via Supabase | DBA | Backend Lead |
| Application Lead | Application restoration | Lead Developer | Sr. Developer |
| Communications Lead | Stakeholder communication | Product Manager | Marketing Director |

### Recovery Time Estimates

| Component | Estimated Recovery Time |
|-----------|-------------------------|
| Infrastructure | 1-2 hours |
| Database (via Supabase PITR) | 30 minutes - 1 hour |
| Application | 30 minutes |
| File Storage | 2-4 hours |
| Complete System | 3-6 hours |

## Documentation and Reporting

### Backup Reports

Automated weekly reports contain:
- Backup success/failure statistics
- Storage utilization
- Retention compliance
- Test restoration results
- Supabase backup status

### Recovery Documentation

After each recovery operation:
1. Document the incident cause
2. Record recovery process and timeline
3. Note any deviations from procedures
4. Document lessons learned
5. Update procedures if necessary

### Compliance Documentation

Maintain documentation for:
- Backup schedule adherence
- Testing schedule adherence
- Recovery time objectives (RTOs)
- Recovery point objectives (RPOs)
- Data retention compliance

## Appendices

### A. Backup Storage Locations

| Environment | Primary Storage | Secondary Storage | Tertiary Storage |
|-------------|----------------|-------------------|------------------|
| Database | Supabase | AWS S3 (us-east-1) | Offsite Physical (Monthly) |
| Media Files | DO Spaces (NYC1) | AWS S3 (us-east-1) | None |
| Application Code | Git Repository | DO Spaces (NYC1) | AWS S3 (us-east-1) |
| Configuration | DO Spaces (NYC1) | AWS S3 (us-east-1) | Offsite Physical (Monthly) |

### B. Retention Policies

| Data Type | Short-term | Mid-term | Long-term | Legal Hold |
|-----------|------------|----------|-----------|------------|
| Database | 7 days (Supabase PITR) | 30 days (manual exports) | 90 days | 7 years |
| User Files | 7 days | 30 days | 90 days | 7 years |
| System Config | 30 days | 90 days | 1 year | 7 years |
| Logs | 7 days | 30 days | 90 days | 7 years |

### C. Recovery Testing Checklist

**Database Recovery Testing:**
- [ ] Supabase Point-in-Time Recovery functionality verified
- [ ] Test recovery completes without errors
- [ ] All tables are present
- [ ] Row counts match expected values
- [ ] Sample queries return expected results
- [ ] Application connects successfully to recovered database

**File Recovery Testing:**
- [ ] Backup file can be accessed
- [ ] Restoration process completes without errors
- [ ] File counts match expected values
- [ ] Sample files are accessible
- [ ] File permissions are correct
- [ ] Application can access restored files

**Full System Recovery Testing:**
- [ ] All components can be restored
- [ ] System starts successfully
- [ ] Services are running
- [ ] External connections work
- [ ] User authentication functions
- [ ] Core business operations work

### D. Contact Information

**Internal Team:**
- IT Emergency: (555) 123-4567
- DevOps On-call: (555) 123-4568
- Database Administrator: (555) 123-4569

**External Providers:**
- Supabase Support: https://supabase.com/support
- Digital Ocean Support: https://cloud.digitalocean.com/support
- AWS Support: https://aws.amazon.com/support
- Datadog Support: https://www.datadoghq.com/support/

---

This Backup & Recovery Procedures document will be reviewed quarterly and updated as needed. Last updated: July 2023. 
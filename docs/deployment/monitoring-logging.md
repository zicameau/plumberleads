# PlumberLeads Monitoring & Logging Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Monitoring Architecture](#monitoring-architecture)
3. [System Metrics](#system-metrics)
4. [Application Metrics](#application-metrics)
5. [Business Metrics](#business-metrics)
6. [Alerting System](#alerting-system)
7. [Dashboards](#dashboards)
8. [Logging Strategy](#logging-strategy)
9. [Log Management](#log-management)
10. [Troubleshooting Guide](#troubleshooting-guide)
11. [Performance Optimization](#performance-optimization)
12. [Appendices](#appendices)

## Introduction

### Purpose
This document outlines the monitoring and logging strategy for the PlumberLeads platform. It describes the tools, metrics, and procedures used to ensure system health, performance, and reliability, as well as to enable effective troubleshooting and operational visibility.

### Scope
This document covers:
- Monitoring architecture and tools
- Key system, application, and business metrics
- Alerting configuration and procedures
- Logging architecture and standards
- Log management and analysis
- Troubleshooting procedures

### References
- System Architecture Document
- Infrastructure Documentation
- Deployment Guide
- Disaster Recovery Plan

## Monitoring Architecture

### Monitoring Stack

```
                    +-------------------+
                    |                   |
                    |  Datadog          |
                    |  (Primary)        |
                    |                   |
                    +--------+----------+
                             |
                   +---------+-----------+
                   |                     |
       +-----------v-----------+  +------v--------------+
       |                       |  |                     |
       |  System Monitoring    |  |  Application APM    |
       |  (Metrics)            |  |  (Traces)           |
       |                       |  |                     |
       +-----------------------+  +---------------------+
                  |                         |
       +----------v-----------+  +----------v----------+
       |                      |  |                     |
       |  Server Agents       |  |  Application SDK    |
       |  (Datadog)           |  |  (Datadog APM)      |
       |                      |  |                     |
       +----------+-----------+  +---------+-----------+
                  |                        |
       +----------v-------------------------v----------+
       |                                              |
       |  Servers                                     |
       |  (Web, Application, Database, Cache, etc.)   |
       |                                              |
       +----------------------------------------------+
```

### Monitoring Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Primary Monitoring | Datadog | Core monitoring and alerting platform |
| Secondary Monitoring | AWS CloudWatch | Redundant monitoring for critical systems |
| Log Management | ELK Stack | Log collection, storage, and analysis |
| APM | Datadog APM | Application performance monitoring |
| RUM | Datadog RUM | Real user monitoring |
| Status Page | Statuspage.io | Public and internal status communication |
| Synthetic Monitoring | Datadog Synthetics | Endpoint and user journey monitoring |

### Monitoring Deployment

**Agent Deployment:**
- Datadog agents installed on all servers via Ansible automation
- Configuration managed through Infrastructure as Code (Terraform)
- Agent update automation via CI/CD pipeline

**Application Instrumentation:**
- Python Flask instrumented with Datadog APM
- Frontend instrumented with Datadog RUM
- Database query monitoring enabled
- Custom metrics for business-specific monitoring

## System Metrics

### Infrastructure Metrics

#### Server Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| CPU Utilization | Datadog Agent | >85% for 5 min | Percentage of CPU in use |
| Memory Usage | Datadog Agent | >90% for 5 min | Percentage of memory in use |
| Disk Usage | Datadog Agent | >85% | Percentage of disk space used |
| Disk I/O | Datadog Agent | >90% of capacity | Disk read/write operations |
| Network I/O | Datadog Agent | >80% of capacity | Network traffic in/out |
| Load Average | Datadog Agent | >system cores x 1.5 | System load average over 1/5/15 min |
| Process Count | Datadog Agent | >500 | Number of running processes |
| Open File Descriptors | Datadog Agent | >85% of max | Number of open file descriptors |

#### Database Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| Connection Count | PostgreSQL Integration | >85% of max | Current active connections |
| Connection Utilization | PostgreSQL Integration | >90% for 5 min | Percentage of connection pool in use |
| Query Performance | PostgreSQL Integration | >1 sec avg | Average query execution time |
| Index Hit Ratio | PostgreSQL Integration | <95% | Percentage of index cache hits |
| Replication Lag | PostgreSQL Integration | >30 sec | Delay between primary and replicas |
| Transaction Rate | PostgreSQL Integration | N/A (trend) | Transactions per second |
| Cache Hit Ratio | PostgreSQL Integration | <90% | Percentage of data found in cache |
| Deadlocks | PostgreSQL Integration | >0 | Number of deadlocks detected |

#### Cache Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| Memory Usage | Redis Integration | >85% | Percentage of Redis memory in use |
| Cache Hit Rate | Redis Integration | <80% | Percentage of cache hits vs misses |
| Evictions | Redis Integration | >0 per sec | Number of keys evicted due to max memory |
| Connected Clients | Redis Integration | >80% of max | Number of connected clients |
| Commands Processed | Redis Integration | N/A (trend) | Commands processed per second |
| Blocked Clients | Redis Integration | >0 for 1 min | Clients blocked waiting for operations |

### Network Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| Load Balancer Requests | DO Integration | N/A (trend) | Requests per second through load balancer |
| HTTP 5xx Errors | Nginx & App Logs | >1% of requests | Server error rate |
| HTTP 4xx Errors | Nginx & App Logs | >5% of requests | Client error rate |
| Response Time | Datadog APM | >500 ms avg | Average response time for requests |
| DNS Resolution Time | Datadog Network | >100 ms | Time to resolve DNS queries |
| CDN Cache Rate | Cloudflare Integration | <80% | Percentage of requests served from CDN |
| SSL Certificate Expiry | Datadog Check | <14 days | Days until SSL certificate expires |

## Application Metrics

### Performance Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| Request Rate | Datadog APM | N/A (trend) | Requests per second to the application |
| Response Time (P95) | Datadog APM | >1 second | 95th percentile response time |
| Response Time (P99) | Datadog APM | >2 seconds | 99th percentile response time |
| Apdex Score | Datadog APM | <0.9 | Application performance satisfaction score |
| Error Rate | Datadog APM | >1% | Percentage of requests resulting in errors |
| CPU Time per Request | Datadog APM | >200 ms | Average CPU time consumed per request |
| Memory per Request | Datadog APM | >50 MB | Average memory consumed per request |
| Database Calls per Request | Datadog APM | >10 | Average DB queries per request |

### Endpoint Performance

| Endpoint | Collection Method | Alert Threshold | Description |
|----------|-------------------|----------------|-------------|
| /api/leads | Datadog APM | >800 ms P95 | Lead listing endpoint performance |
| /api/plumbers/profile | Datadog APM | >600 ms P95 | Profile management endpoint performance |
| /api/auth/login | Datadog APM | >400 ms P95 | Login endpoint performance |
| /api/payments | Datadog APM | >1000 ms P95 | Payment processing endpoint performance |
| /api/admin/* | Datadog APM | >800 ms P95 | Admin endpoints performance |

### Frontend Performance

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| Page Load Time | Datadog RUM | >3 seconds | Full page load time |
| First Contentful Paint | Datadog RUM | >1.8 seconds | Time to first content rendering |
| Largest Contentful Paint | Datadog RUM | >2.5 seconds | Time to largest content element |
| First Input Delay | Datadog RUM | >100 ms | Time to interactivity |
| Cumulative Layout Shift | Datadog RUM | >0.1 | Visual stability score |
| JS Errors | Datadog RUM | >0 | JavaScript errors on frontend |
| AJAX Error Rate | Datadog RUM | >1% | Percentage of failed AJAX requests |

### Synthetic Checks

| Check | Frequency | Alert Threshold | Description |
|-------|-----------|----------------|-------------|
| Home Page Availability | 1 min | >99.9% uptime | Checks if home page loads correctly |
| Login Flow | 5 min | >99.5% success | Tests end-to-end login functionality |
| Lead Claiming Process | 10 min | >99% success | Tests lead claiming workflow |
| Payment Processing | 15 min | >99% success | Tests payment submission flow |
| Admin Dashboard | 30 min | >99.5% success | Tests admin interface availability |
| Mobile Responsive Check | 60 min | >99% success | Tests responsive behavior on mobile devices |

## Business Metrics

### User Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| Active Users | Application Custom | <previous day -20% | Number of active users per day |
| New Registrations | Application Custom | <previous day -30% | Number of new plumber registrations |
| Registration Completion Rate | Application Custom | <80% | Percentage of started registrations completed |
| Session Duration | Datadog RUM | N/A (trend) | Average user session time |
| Mobile vs Desktop | Datadog RUM | N/A (trend) | Ratio of mobile to desktop users |
| Geographic Distribution | Datadog RUM | N/A (trend) | User locations by region |

### Lead Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| New Leads | Application Custom | <previous day -20% | Number of new leads generated |
| Lead Claim Rate | Application Custom | <60% | Percentage of leads being claimed |
| Time to Claim | Application Custom | >30 min avg | Average time for leads to be claimed |
| Lead Quality Score | Application Custom | <4.0/5.0 avg | Average quality rating of leads |
| Lead Distribution | Application Custom | N/A (trend) | Lead distribution by service type/area |
| Disputed Leads | Application Custom | >5% of total | Percentage of leads disputed |

### Payment Metrics

| Metric | Collection Method | Alert Threshold | Description |
|--------|-------------------|----------------|-------------|
| Transaction Volume | Application Custom | <previous day -25% | Number of payment transactions |
| Transaction Value | Application Custom | <previous day -25% | Total value of transactions |
| Failed Payments | Application Custom | >5% of attempts | Percentage of payment attempts failing |
| Refund Rate | Application Custom | >3% of transactions | Percentage of payments refunded |
| Average Transaction Value | Application Custom | <previous month -10% | Average value per transaction |
| Payment Method Distribution | Application Custom | N/A (trend) | Distribution of payment methods used |

## Alerting System

### Alert Severity Levels

| Severity | Description | Response Time | Notification Method |
|----------|-------------|---------------|---------------------|
| P1 (Critical) | Service outage or severe degradation | Immediate (24/7) | PagerDuty, SMS, Email, Slack |
| P2 (High) | Major functionality impacted | Within 30 minutes (business hours) | PagerDuty, Email, Slack |
| P3 (Medium) | Minor functionality impacted | Within 8 hours (business hours) | Email, Slack |
| P4 (Low) | Non-critical issues | Next business day | Email |

### Alert Routes

| Component | P1 Alert Recipient | P2-P4 Alert Recipient |
|-----------|--------------------|-----------------------|
| Infrastructure | On-call DevOps | DevOps Team |
| Application | On-call Developer | Development Team |
| Database | On-call DBA | Database Team |
| Security | On-call Security | Security Team |
| Business Metrics | N/A | Product Team |

### Alert Lifecycle

1. **Alert Triggered**
   - Incident created in monitoring system
   - Notification sent based on severity
   - Initial acknowledgment required

2. **Incident Response**
   - Responder acknowledges alert
   - Investigation begins
   - Status updates posted to incident channel

3. **Resolution**
   - Issue resolved
   - Alert cleared
   - Post-mortem scheduled if needed

4. **Post-Incident**
   - Incident documentation completed
   - Post-mortem conducted for P1/P2 incidents
   - Monitoring improvements identified

### Alert Noise Reduction

- **Alert Grouping**: Related alerts grouped into a single incident
- **Alert Dampening**: Alerts require conditions to persist for defined duration
- **Maintenance Windows**: Scheduled maintenance periods suppress non-critical alerts
- **Alert Tuning**: Regular review and refinement of thresholds
- **Correlation Rules**: Related alerts are combined based on correlation rules

## Dashboards

### Primary Dashboards

#### Executive Dashboard
- System health overview
- SLA compliance metrics
- User growth trends
- Revenue metrics
- Key business KPIs

#### Operations Dashboard
- Infrastructure health
- Application performance
- Error rates and distribution
- Active incidents
- Resource utilization

#### Development Dashboard
- Deployment frequency
- Deploy success rate
- Code coverage
- Technical debt metrics
- Error trends by service

#### On-call Dashboard
- Current alert status
- Recent incidents
- Performance anomalies
- Common failure points
- Quick access to logs

### Specialized Dashboards

#### Database Performance
- Query performance
- Connection utilization
- Replication status
- Backup status
- Storage trends

#### Frontend Performance
- Page load metrics
- User experience scores
- Browser error rates
- Client-side performance
- Geographic distribution

#### Payment Processing
- Transaction success rate
- Payment gateway latency
- Error breakdown by type
- Fraud detection metrics
- Refund monitoring

#### Lead Management
- Lead generation rate
- Lead distribution by area
- Claim time metrics
- Quality scores
- Dispute tracking

## Logging Strategy

### Logging Levels

| Level | When to Use | Examples |
|-------|-------------|----------|
| ERROR | Errors that prevent functionality | Failed payments, database connection failures |
| WARN | Potential issues to watch | Slow queries, retry attempts, edge cases |
| INFO | Normal operation events | User logins, lead claiming, configuration changes |
| DEBUG | Detailed information for troubleshooting | Request/response details, function parameters |
| TRACE | Extensive debugging information | Full execution paths, variable state changes |

### Logging Standards

**Log Format:**
```
{timestamp} {level} {service} {trace_id} {source} {message} {context}
```

**Context Information:**
- `timestamp`: ISO 8601 format with milliseconds
- `level`: Log level (ERROR, WARN, INFO, DEBUG, TRACE)
- `service`: Service or component name
- `trace_id`: Unique identifier for request tracing
- `source`: File/class and line number
- `message`: Human-readable log message
- `context`: JSON object with additional contextual data

**Sensitive Data Handling:**
- PII must be redacted (emails, names, phone numbers)
- Financial data must be masked (credit card numbers, bank details)
- Authentication credentials must never be logged
- User IDs may be logged for correlation purposes

### Application Logging

**Web Server Logs:**
- Access logs in combined format
- Error logs for server-level issues
- Request timing information
- SSL/TLS connection details

**Application Logs:**
- Request/response metadata (not full payloads)
- Authentication events
- Business operations (lead creation, claiming)
- Background job execution
- Payment processing events (not card details)
- Third-party integration calls

**Database Logs:**
- Slow query logs (queries exceeding 500ms)
- Connection events
- Schema changes
- Backup operations
- Replication status

## Log Management

### Log Collection

**Collection Architecture:**

```
    +---------------+    +---------------+    +---------------+
    |               |    |               |    |               |
    |  Application  |    |  Database     |    |  Web Server   |
    |  Logs         |    |  Logs         |    |  Logs         |
    |               |    |               |    |               |
    +-------+-------+    +-------+-------+    +-------+-------+
            |                    |                    |
            v                    v                    v
    +-------+--------------------+--------------------+-------+
    |                                                        |
    |               Filebeat Collectors                      |
    |                                                        |
    +------------------------+-------------------------------+
                            |
                            v
                  +---------+---------+
                  |                   |
                  |    Logstash       |
                  |    Processing     |
                  |                   |
                  +---------+---------+
                            |
                            v
              +-------------+-------------+
              |                           |
    +---------+---------+     +-----------+---------+
    |                   |     |                     |
    |  Elasticsearch    |     |   Kibana            |
    |  Storage          |     |   Visualization     |
    |                   |     |                     |
    +-------------------+     +---------------------+
```

**Collection Methods:**
- Log files collected via Filebeat agents
- Structured logging (JSON) for application logs
- Syslog collection for infrastructure logs
- Kubernetes pod logs collected via Filebeat DaemonSet
- Cloud service logs via API integration

### Log Processing

**Processing Pipeline:**
1. **Collection**: Raw logs gathered from all sources
2. **Parsing**: Structured data extracted from log formats
3. **Enrichment**: Additional context added (GeoIP, service mapping)
4. **Normalization**: Field names standardized across sources
5. **Filtering**: Sensitive data removed or masked
6. **Indexing**: Processed logs stored in Elasticsearch

**Common Transformations:**
- Timestamp normalization to UTC
- User ID correlation
- Session tracking
- Request path normalization
- Error categorization
- Performance metric extraction

### Log Retention

| Log Type | Hot Storage | Warm Storage | Cold Storage |
|----------|-------------|--------------|--------------|
| Application Logs | 7 days | 30 days | 1 year |
| Web Server Logs | 3 days | 15 days | 90 days |
| Database Logs | 7 days | 30 days | 180 days |
| Security Logs | 30 days | 90 days | 2 years |
| System Logs | 7 days | 30 days | 90 days |

**Storage Optimization:**
- Log compression for long-term storage
- Index lifecycle management
- Selective field retention for cold storage
- Aggregate summaries for historical analysis

### Log Analysis

**Analysis Tools:**
- Kibana dashboards for visualization
- Saved queries for common investigations
- Alert rules based on log patterns
- Machine learning for anomaly detection

**Common Analysis Patterns:**
- Error spike detection
- User journey tracing
- Performance bottleneck identification
- Security incident investigation
- Feature usage analysis

## Troubleshooting Guide

### Common Issues and Resolution Steps

#### High Application Response Time

**Investigation Steps:**
1. Check application APM dashboards for anomalies
2. Identify slowest endpoints or transactions
3. Correlate with system metrics (CPU, memory)
4. Check database query performance
5. Analyze recent code deployments

**Resolution Actions:**
- Scale application servers if under resource pressure
- Optimize identified slow database queries
- Check for network latency issues
- Investigate application memory leaks

#### Database Performance Issues

**Investigation Steps:**
1. Check PostgreSQL dashboard for key metrics
2. Review slow query logs
3. Examine connection pool utilization
4. Check for blocking transactions
5. Verify index usage on common queries

**Resolution Actions:**
- Optimize identified problematic queries
- Add missing indexes
- Tune database configuration parameters
- Increase connection pool if needed
- Consider read replicas for read-heavy operations

#### Payment Processing Failures

**Investigation Steps:**
1. Check Stripe dashboard for error messages
2. Review application logs for payment attempts
3. Verify webhook delivery status
4. Check for API rate limiting

**Resolution Actions:**
- Address specific error codes from payment provider
- Verify API credentials are valid
- Check for network connectivity issues
- Implement retry mechanism for transient failures

### Log Search Examples

#### Finding Failed Login Attempts
```
level:ERROR AND service:auth AND message:"Failed login attempt" AND context.ip_address:*
```

#### Tracking a User's Journey
```
trace_id:"abc123def456" AND NOT level:DEBUG
```

#### Identifying Slow API Requests
```
service:api AND context.duration:>500 AND level:WARN
```

#### Investigating Payment Failures
```
service:payment AND level:ERROR AND message:"Payment processing failed" AND context.error_code:*
```

## Performance Optimization

### Monitoring-Driven Optimization

**Identification Process:**
1. Use APM to identify slowest endpoints
2. Analyze transaction traces for bottlenecks
3. Review database query performance
4. Examine resource utilization patterns
5. Test user-impacting operations with synthetics

**Optimization Cycle:**
1. Identify performance issues through monitoring
2. Prioritize based on user impact
3. Implement optimizations
4. Measure before/after performance
5. Document improvements

### Common Optimizations

#### Application Optimizations

| Issue | Detection Method | Common Solutions |
|-------|------------------|------------------|
| N+1 Query Problems | APM Database Tracing | Implement eager loading, optimize ORM usage |
| Memory Leaks | Memory Growth Over Time | Fix object retention issues, optimize memory usage |
| Slow API Endpoints | APM Transaction Traces | Cache results, optimize algorithms, refactor code |
| High CPU Usage | System Metrics | Optimize computation, implement caching, consider async processing |
| Connection Pool Exhaustion | Database Metrics | Increase pool size, reduce connection holding time |

#### Infrastructure Optimizations

| Issue | Detection Method | Common Solutions |
|-------|------------------|------------------|
| Resource Constraints | System Metrics | Scale up/out, optimize resource usage |
| Network Latency | Network Metrics | CDN usage, endpoint collocation, connection pooling |
| Database Bottlenecks | Database Metrics | Query optimization, indexing, read replicas |
| Cache Inefficiency | Cache Hit Rate | Adjust TTL, optimize cache keys, increase cache size |
| Load Distribution | Server Load Balance | Adjust load balancer algorithm, check for "hot" nodes |

## Appendices

### A. Tool Configuration Examples

#### Datadog Agent Configuration
```yaml
# /etc/datadog-agent/datadog.yaml
api_key: YOUR_API_KEY
hostname: pl-prod-web-01
tags:
  - env:production
  - service:web
  - role:application
logs_enabled: true
apm_config:
  enabled: true
process_config:
  enabled: true
```

#### Logging Configuration (Python)
```python
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "plumberleads-api",
            "trace_id": getattr(record, "trace_id", "unknown"),
            "source": f"{record.pathname}:{record.lineno}",
            "message": record.getMessage(),
            "context": getattr(record, "context", {})
        }
        return json.dumps(log_record)

# Logger setup
logger = logging.getLogger("plumberleads")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### B. Alert Configuration Examples

#### Critical CPU Alert
```yaml
name: High CPU Usage
type: metric alert
query: avg(last_5m):avg:system.cpu.user{service:web} by {host} > 85
message: |
  High CPU usage detected on {{host.name}}
  
  CPU usage: {{value}}%
  
  @pagerduty-devops @slack-ops-alerts
monitor_options:
  notify_audit: true
  locked: false
  timeout_h: 0
  new_host_delay: 300
  require_full_window: true
  notify_no_data: false
  renotify_interval: 60
  escalation_message: "CPU usage still critical on {{host.name}} - please investigate!"
  thresholds:
    critical: 85
    warning: 75
```

#### API Error Rate Alert
```yaml
name: High API Error Rate
type: metric alert
query: sum(last_5m):sum:plumberleads.api.errors{*} / sum:plumberleads.api.requests{*} * 100 > 1
message: |
  High API error rate detected!
  
  Current error rate: {{value}}%
  
  @pagerduty-developers @slack-dev-alerts
monitor_options:
  notify_audit: true
  locked: false
  timeout_h: 0
  require_full_window: false
  notify_no_data: true
  renotify_interval: 30
  thresholds:
    critical: 1
    warning: 0.5
```

### C. Dashboard Templates

#### System Health Dashboard JSON
```json
{
  "title": "System Health Overview",
  "description": "Key metrics for system health monitoring",
  "widgets": [
    {
      "title": "CPU Usage by Host",
      "definition": {
        "type": "timeseries",
        "requests": [
          {
            "q": "avg:system.cpu.user{service:web} by {host}",
            "display_type": "line"
          }
        ]
      }
    },
    {
      "title": "Memory Usage by Host",
      "definition": {
        "type": "timeseries",
        "requests": [
          {
            "q": "avg:system.mem.used{service:web} by {host} / avg:system.mem.total{service:web} by {host} * 100",
            "display_type": "line"
          }
        ]
      }
    }
    // Additional widgets omitted for brevity
  ]
}
```

### D. Monitoring Health Check

**Weekly Monitoring Review Checklist:**
1. Alert Review
   - Check for noisy alerts that need tuning
   - Review missed incidents
   - Verify alert thresholds are appropriate

2. Dashboard Review
   - Verify all critical dashboards are functional
   - Check for missing or outdated metrics
   - Update dashboards for new services/features

3. Logging Review
   - Verify log collection is working for all services
   - Check log retention and storage usage
   - Review log-based alerts

4. Synthetic Check Review
   - Verify all critical synthetic tests are passing
   - Update tests for new features
   - Check for flaky tests that need stabilization

---

This Monitoring & Logging Documentation will be reviewed and updated quarterly to ensure it reflects current practices and tooling. Last updated: July 2023. 
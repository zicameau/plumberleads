# PlumberLeads Admin User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Admin Dashboard Overview](#admin-dashboard-overview)
3. [User Management](#user-management)
4. [Lead Management](#lead-management)
5. [Payment Management](#payment-management)
6. [Reports and Analytics](#reports-and-analytics)
7. [System Configuration](#system-configuration)
8. [Marketing Integration](#marketing-integration)
9. [Support Management](#support-management)
10. [Security and Compliance](#security-and-compliance)
11. [Troubleshooting](#troubleshooting)

## Introduction

Welcome to the PlumberLeads Admin Manual. This document provides comprehensive instructions for administrators to effectively manage the PlumberLeads platform. As an administrator, you have access to powerful tools for managing users, leads, payments, and system settings.

### Purpose of This Manual

This manual will guide you through:
- Managing plumber accounts and their verification
- Overseeing lead generation, distribution, and quality
- Handling payments, refunds, and financial reports
- Configuring system settings and integrations
- Monitoring platform performance and security

### Access Levels

The PlumberLeads platform has two primary user roles:
- **Admin**: Full access to all platform features and settings
- **Plumber**: Access limited to their own profile, available leads, and claimed leads

Some admin accounts may have specialized permissions for specific sections.

## Admin Dashboard Overview

### Accessing the Admin Dashboard

1. Navigate to [plumberleads.com/admin](https://plumberleads.com/admin)
2. Enter your admin credentials (email and password)
3. Use two-factor authentication if enabled (recommended)

### Dashboard Layout

![Admin Dashboard](../assets/images/admin-dashboard.png)

The admin dashboard consists of:

1. **Navigation Sidebar**: Access to all administrative sections
2. **Quick Stats**: Overview of key metrics
   - Active plumbers
   - Available leads
   - Today's claimed leads
   - Revenue this month
3. **Recent Activity**: Latest actions on the platform
4. **System Alerts**: Important notifications requiring attention
5. **Quick Actions**: Common administrative tasks

## User Management

### Viewing Plumber Accounts

1. Click **Users** in the navigation sidebar
2. View the list of plumber accounts
3. Use filters to sort by:
   - Registration date
   - Status (active, pending, suspended)
   - Location (service area)
   - Subscription type

### Reviewing New Registrations

1. Click **Users** > **Pending Verification**
2. Review each pending plumber's information:
   - Personal and company details
   - License information
   - Insurance documentation
3. Click on a plumber's name to view their full profile

### Verifying Plumbers

1. Open the plumber's profile from the pending list
2. Review uploaded documents (plumbing license, insurance, etc.)
3. Click "Verify Documents" if everything is in order
4. Add notes if needed in the "Admin Notes" section
5. Click "Approve" to activate the account or "Reject" with a reason
6. The system will automatically notify the plumber of your decision

### Managing Existing Accounts

1. Click **Users** > **All Plumbers**
2. Search for a specific plumber using the search box
3. Click on a plumber's name to view/edit their profile
4. Available actions:
   - Edit account details
   - Reset password
   - Adjust service areas
   - View claimed leads
   - View payment history
   - Suspend/reactivate account

### Suspending or Deactivating Accounts

1. Navigate to the plumber's profile
2. Click "Account Actions" dropdown
3. Select "Suspend Account" or "Deactivate Account"
4. Enter a reason for the action
5. Click "Confirm"
6. The system will notify the plumber via email

## Lead Management

### Viewing All Leads

1. Click **Leads** in the navigation sidebar
2. View leads with their current status (available, claimed, completed)
3. Filter leads by:
   - Status
   - Date range
   - Service area
   - Service type
   - Source (Facebook, Google, etc.)

### Creating Manual Leads

1. Click **Leads** > **Create Lead**
2. Fill in the lead information:
   - Customer details (name, contact information)
   - Service required
   - Location/service area
   - Job description
   - Lead priority
3. Set lead pricing
4. Select "Notify all eligible plumbers" if desired
5. Click "Create Lead"

### Editing Lead Details

1. Find the lead in the leads list
2. Click on the lead ID to open details
3. Click "Edit" button
4. Modify the required fields
5. Click "Save Changes"
6. Select whether to notify plumbers of changes

### Managing Lead Quality Issues

1. Navigate to **Leads** > **Reported Issues**
2. Review reported issues from plumbers
3. For each report:
   - Review the plumber's comments
   - Check customer information for accuracy
   - Contact the customer if necessary to verify information
4. Take appropriate action:
   - Deny the report (no issue found)
   - Update lead information (if incorrect)
   - Issue refund (if lead was invalid)
   - Remove lead (if fraudulent)

### Setting Lead Pricing

1. Go to **Settings** > **Lead Pricing**
2. Configure pricing rules:
   - Base prices by service type
   - Location multipliers
   - Urgency factors
   - Special event adjustments
3. Set minimum and maximum prices
4. Click "Save Pricing Rules"

## Payment Management

### Viewing Payment History

1. Click **Payments** in the navigation sidebar
2. View all transactions across the platform
3. Filter by:
   - Date range
   - Amount
   - Status (successful, failed, refunded)
   - Plumber
   - Lead ID

### Processing Refunds

1. Go to **Payments** > **Refund Requests**
2. Review each refund request:
   - Plumber information
   - Lead details
   - Reason for refund request
   - Supporting information
3. Click "Approve" to process the refund or "Deny" with a reason
4. For approved refunds:
   - Enter full or partial refund amount
   - Add admin notes
   - Click "Process Refund"

### Managing Payment Settings

1. Navigate to **Settings** > **Payment Configuration**
2. Configure:
   - Payment gateway settings (Stripe)
   - Currency options
   - Payment methods allowed
   - Automatic refund rules
   - Invoice templates

## Reports and Analytics

### Dashboard Analytics

1. Click **Reports** in the navigation sidebar
2. View the main analytics dashboard with:
   - Daily/weekly/monthly lead volume
   - Claim rates by area
   - Revenue trends
   - Plumber activity levels

### Generating Custom Reports

1. Go to **Reports** > **Custom Reports**
2. Select report type:
   - Lead performance
   - Revenue
   - Plumber activity
   - Marketing channel effectiveness
3. Set date range and filters
4. Click "Generate Report"
5. View on screen or export to CSV/PDF

### Lead Source Analysis

1. Navigate to **Reports** > **Marketing Performance**
2. View metrics by acquisition channel:
   - Cost per lead
   - Lead quality score
   - Conversion rate
   - ROI by channel
3. Use filters to focus on specific date ranges or locations

### Financial Reports

1. Go to **Reports** > **Financial**
2. Access financial reports:
   - Monthly revenue
   - Transaction summaries
   - Refund rates
   - Revenue by service area/type
3. Export data for accounting purposes

## System Configuration

### General Settings

1. Navigate to **Settings** > **General**
2. Configure:
   - Platform name and branding
   - Contact information
   - Time zone settings
   - Default language
   - Terms of service and privacy policy

### Email Templates

1. Go to **Settings** > **Email Templates**
2. Edit templates for:
   - Welcome emails
   - Lead notifications
   - Payment receipts
   - Refund notifications
   - Account verification
3. Use the HTML editor to customize content
4. Insert dynamic variables as needed
5. Send test emails to verify appearance

### Service Areas Management

1. Navigate to **Settings** > **Service Areas**
2. Add, edit, or remove service areas
3. Define boundaries by:
   - City/region
   - Zip/postal codes
   - Custom geographical boundaries
4. Set special rules for particular areas

### Service Types Configuration

1. Go to **Settings** > **Service Types**
2. Manage plumbing service categories:
   - Add new service types
   - Edit existing types
   - Set default pricing
   - Define display order

## Marketing Integration

### Managing Ad Platforms

1. Navigate to **Marketing** > **Ad Platforms**
2. Configure connections to:
   - Facebook Ads
   - Google Ads
   - Other ad platforms
3. Set API keys and credentials
4. Define conversion tracking

### Lead Form Configuration

1. Go to **Marketing** > **Lead Forms**
2. Create and edit web forms for lead capture
3. Configure:
   - Required fields
   - Custom questions
   - Thank you messages
   - Redirect options
4. Get embed codes for website integration

### Tracking Pixel Management

1. Navigate to **Marketing** > **Tracking**
2. Set up and manage:
   - Facebook Pixel
   - Google Analytics
   - Conversion tracking
   - Custom events

## Support Management

### Viewing Support Requests

1. Click **Support** in the navigation sidebar
2. View all incoming support requests
3. Sort by:
   - Date
   - Status (new, in progress, resolved)
   - Priority
   - Type (account, payment, lead, technical)

### Responding to Support Tickets

1. Click on a ticket to view details
2. Review the user's issue and account information
3. Add internal notes visible only to admins
4. Compose a response
5. Select status (in progress, resolved, etc.)
6. Click "Send Response"

### Common Support Actions

- Reset passwords
- Adjust lead claim issues
- Process manual refunds
- Provide account credit
- Verify documentation
- Update plumber information

## Security and Compliance

### User Audit Log

1. Navigate to **Security** > **Audit Log**
2. View all administrator actions:
   - User changes
   - Lead modifications
   - Payment adjustments
   - Setting changes
3. Filter by:
   - Admin user
   - Action type
   - Date range

### Data Privacy Management

1. Go to **Security** > **Privacy**
2. Manage:
   - Data deletion requests
   - Data export requests
   - Privacy policy settings
   - Cookie consent configuration

### Access Control

1. Navigate to **Security** > **Admin Users**
2. Manage admin accounts:
   - Create new admin users
   - Edit permissions
   - Deactivate accounts
   - Reset passwords
3. Configure role-based access controls

## Troubleshooting

### Common Issues and Solutions

#### Lead Distribution Problems
- Verify service area settings
- Check plumber status and verification
- Ensure lead pricing is correctly configured

#### Payment Processing Issues
- Verify Stripe connection status
- Check payment method details
- Review transaction logs

#### Email Delivery Problems
- Verify SendGrid connection
- Check email templates for errors
- Review bounce/complaint reports

### System Status

1. Go to **Settings** > **System Status**
2. View:
   - API service status
   - Database performance
   - Third-party integrations
   - Recent errors or warnings

### Contacting Technical Support

For issues beyond administrative control, contact technical support:
- Email: tech-support@plumberleads.com
- Emergency Phone: (555) 123-4568
- Include: Admin username, issue description, and screenshots if relevant

## Maintenance Procedures

### Cache Management

1. Navigate to **Settings** > **Maintenance**
2. Click "Clear Cache" to refresh system data

### Backup and Restore

1. Go to **Settings** > **Maintenance**
2. To create a manual backup:
   - Click "Create Backup"
   - Select components (database, files, settings)
   - Click "Start Backup"
3. To restore from backup:
   - Select a backup from the list
   - Click "Restore"
   - Confirm the action

---

**Note**: This manual covers standard administrative operations. For development-related tasks, please refer to the Technical Documentation. 
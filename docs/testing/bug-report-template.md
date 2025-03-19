# PlumberLeads Bug Report Template

## Overview

This document provides a standardized template for reporting bugs in the PlumberLeads platform. Using this template ensures that all necessary information is included to effectively reproduce, diagnose, and fix issues.

## When to Use This Template

Use this template when:
- You encounter unexpected behavior in the PlumberLeads platform
- A feature is not functioning as specified in the requirements
- You find UI/UX inconsistencies or issues
- Performance or security concerns are identified

## Bug Report Format

### Bug ID
*[Automatically assigned by the bug tracking system]*

### Report Date
*[YYYY-MM-DD]*

### Reported By
*[Your Name]*

### Severity
- [ ] Critical - System crash, data loss, security breach
- [ ] High - Major function not working, no workaround
- [ ] Medium - Function not working as expected, has workaround
- [ ] Low - Minor issues that don't impact functionality

### Priority
- [ ] Urgent - Fix immediately (blocker)
- [ ] High - Fix in the current sprint
- [ ] Medium - Fix in the next sprint
- [ ] Low - Fix when time permits

### Environment
**Platform Version:** *[e.g., v1.2.3]*

**Browser/Device:**
- Browser: *[e.g., Chrome 96.0.4664.110, Firefox 95.0, Safari 15.1]*
- OS: *[e.g., Windows 10, macOS Monterey, iOS 15, Android 12]*
- Device: *[e.g., Desktop, iPhone 13, Samsung Galaxy S21]*
- Screen Resolution: *[e.g., 1920x1080]*

**Server Environment:** *[e.g., Production, Staging, Development]*

### Bug Title
*[Brief, descriptive title of the issue]*

### Bug Description
*[Detailed description of the issue, including what happened vs. what was expected]*

### Steps to Reproduce
1. *[First step - be specific]*
2. *[Second step]*
3. *[And so on...]*

### Expected Result
*[What should happen when the steps are followed]*

### Actual Result
*[What actually happened when the steps were followed]*

### Visual Proof
*[Attach screenshots, videos, or links that demonstrate the issue]*

### User Impact
*[Describe how this bug affects users or business operations]*

### Frequency
- [ ] Always reproducible
- [ ] Frequently reproducible
- [ ] Occasionally reproducible
- [ ] Rarely reproducible (provide circumstances if known)

### Regression
*[Is this a new issue or a regression? If regression, in what version did it last work correctly?]*

### Related Issues
*[Links to related bugs, user stories, or documentation]*

## Additional Information

### Console Logs
```
[Paste any relevant console logs, error messages, or stack traces here]
```

### Network Requests
*[Include relevant network requests/responses if applicable]*

### Database Queries
*[Include relevant database queries if applicable]*

### Workaround
*[Describe any temporary workaround for the issue, if known]*

### Suggested Fix
*[If you have insights into what might be causing the issue or how to fix it, note them here]*

---

## Template Examples

### Example 1: Critical Bug

**Bug ID:** BUG-123

**Report Date:** 2023-07-15

**Reported By:** Jane Smith

**Severity:** Critical

**Priority:** Urgent

**Environment:**
- Platform Version: v1.5.2
- Browser: Chrome 114.0.5735.198
- OS: Windows 11
- Device: Desktop
- Screen Resolution: 1920x1080
- Server Environment: Production

**Bug Title:** Payment processing system down - all lead claims failing

**Bug Description:** The payment processing system is completely non-functional. When plumbers attempt to claim leads, the payment processing fails with a 500 error. No leads can be claimed, severely impacting business operations.

**Steps to Reproduce:**
1. Log in as any plumber account
2. Navigate to Available Leads
3. Select any lead and click "Claim Lead"
4. Enter payment details and submit

**Expected Result:** Payment should process and lead should be claimed successfully.

**Actual Result:** The system returns a 500 error and displays "Payment processing failed. Please try again later." No leads can be claimed.

**Visual Proof:** [Screenshot of error message attached]

**User Impact:** Critical business impact. Plumbers cannot claim any leads, resulting in lost revenue and poor user experience. Customers with emergency plumbing needs cannot be connected with plumbers.

**Frequency:** Always reproducible

**Regression:** Yes, this functionality was working in v1.5.1 released yesterday.

**Related Issues:** Related to the recent Stripe API integration update (FEAT-456)

**Console Logs:**
```
POST https://plumberleads.com/api/payments 500 (Internal Server Error)
Uncaught TypeError: Cannot read properties of undefined (reading 'id')
    at processPayment (payment.js:132)
    at claimLead (leads.js:89)
```

**Network Requests:**
```
Request URL: https://plumberleads.com/api/payments
Request Method: POST
Status Code: 500 Internal Server Error
Response: {"error":{"code":"stripe_connection_error","message":"Could not connect to Stripe API"}}
```

**Workaround:** None currently available. Plumbers cannot claim leads.

**Suggested Fix:** The error seems related to the recent Stripe API integration update. Check Stripe API credentials and connectivity. The error logs suggest the Stripe connection is failing.

### Example 2: Medium Bug

**Bug ID:** BUG-456

**Report Date:** 2023-07-16

**Reported By:** John Doe

**Severity:** Medium

**Priority:** Medium

**Environment:**
- Platform Version: v1.5.2
- Browser: Safari 15.6
- OS: iOS 15.5
- Device: iPhone 13
- Screen Resolution: 390x844
- Server Environment: Production

**Bug Title:** Service area selection doesn't save on mobile devices

**Bug Description:** When using the mobile interface, plumbers cannot save changes to their service areas. The save button appears to work (shows loading indicator), but upon refreshing or returning to the page, the changes are not persisted.

**Steps to Reproduce:**
1. Log in as a plumber on a mobile device
2. Navigate to Profile > Service Areas
3. Add or remove a service area
4. Click "Save Changes"
5. Navigate away and return to the Service Areas page

**Expected Result:** Changes to service areas should be saved and displayed when returning to the page.

**Actual Result:** The service areas revert to their previous state, and changes are not saved.

**Visual Proof:** [Screen recording showing the issue attached]

**User Impact:** Plumbers using mobile devices cannot update their service areas, potentially missing leads in areas they serve.

**Frequency:** Always reproducible on iOS devices, occasionally on Android devices

**Regression:** New issue in v1.5.2, worked correctly in v1.5.1

**Related Issues:** May be related to the UI responsive design update (FEAT-789)

**Console Logs:**
```
PUT https://plumberleads.com/api/plumbers/profile/service-areas 200 (OK)
Warning: Form submission canceled because the form is not connected
```

**Network Requests:**
```
Request URL: https://plumberleads.com/api/plumbers/profile/service-areas
Request Method: PUT
Status Code: 200 OK
Request Payload: {"service_areas":["Los Angeles","Beverly Hills","Santa Monica"]}
Response: {"success":true}
```

**Workaround:** Plumbers can update their service areas using the desktop version of the site.

**Suggested Fix:** The network request shows a successful response, but the data isn't being properly refreshed or stored in the client-side state. Check the mobile form submission handler and state management.

## Instructions for Using This Template

1. **Create a new bug report** in the bug tracking system (JIRA)
2. **Copy and paste** this template into the description field
3. **Fill in all applicable sections** with as much detail as possible
4. **Attach visual evidence** such as screenshots or videos
5. **Assign the appropriate severity and priority** based on impact
6. **Submit the bug** to the development team

## Best Practices for Bug Reporting

1. **Be specific and concise** - Provide clear, factual information
2. **One bug per report** - Don't combine multiple issues into one report
3. **Provide reproducible steps** - Make it easy for developers to recreate the issue
4. **Include environment details** - Browser, OS, and device information are crucial
5. **Attach visual evidence** - Screenshots or videos that demonstrate the issue
6. **Avoid assumptions** - Report what you observe, not what you think caused it
7. **Test in multiple environments** - If possible, verify if the bug exists in different browsers/devices
8. **Check for duplicates** - Search for existing reports before creating a new one

## Bug Lifecycle

1. **New** - Bug is reported but not yet reviewed
2. **Triaged** - Bug has been reviewed and prioritized
3. **In Progress** - Developer is actively working on a fix
4. **Fixed** - Developer has implemented a solution
5. **Verified** - QA has confirmed the fix works
6. **Closed** - Bug is considered resolved
7. **Reopened** - Issue has recurred after being closed

---

This template is maintained by the QA team. Last updated: July 2023. 
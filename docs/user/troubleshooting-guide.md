# PlumberLeads Troubleshooting Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Common Login Issues](#common-login-issues)
3. [Lead Management Issues](#lead-management-issues)
4. [Payment Problems](#payment-problems)
5. [Profile and Account Settings](#profile-and-account-settings)
6. [Notification Troubleshooting](#notification-troubleshooting)
7. [Mobile Access Issues](#mobile-access-issues)
8. [Performance Problems](#performance-problems)
9. [Error Message Reference](#error-message-reference)
10. [System Status and Maintenance](#system-status-and-maintenance)
11. [Getting Support](#getting-support)

## Introduction

This troubleshooting guide is designed to help both plumbers and administrators quickly resolve common issues with the PlumberLeads platform. The guide provides step-by-step instructions for diagnosing and fixing problems without needing to contact support.

## Common Login Issues

### Unable to Login

**Symptoms:**
- Login form returns "Invalid credentials" message
- Unable to access your account despite correct credentials

**Troubleshooting Steps:**
1. **Verify your email and password:**
   - Ensure caps lock is not enabled
   - Check for extra spaces before or after your email or password
   - Try the "Forgot Password" option to reset your password

2. **Clear browser cache and cookies:**
   ```
   Chrome: Settings > Privacy and Security > Clear browsing data
   Firefox: Options > Privacy & Security > Cookies and Site Data > Clear Data
   Safari: Preferences > Privacy > Manage Website Data > Remove All
   ```

3. **Try an alternate browser:**
   - If you can log in with a different browser, your primary browser may have corrupted data

4. **Check for account status issues:**
   - Your account may be suspended or pending verification
   - Contact support if you believe your account should be active

### Session Timeout Issues

**Symptoms:**
- Frequently being logged out during active use
- "Your session has expired" messages

**Troubleshooting Steps:**
1. **Check browser settings:**
   - Ensure cookies are enabled in your browser
   - Disable any privacy extensions that might be clearing cookies

2. **Adjust security software:**
   - Some antivirus or security software may be clearing session cookies
   - Add plumberleads.com to your trusted sites

3. **Network issues:**
   - Unstable internet connections can cause authentication problems
   - Try connecting to a different network

## Lead Management Issues

### Unable to See Available Leads

**Symptoms:**
- The available leads section is empty despite being in an active service area
- Message stating "No leads found in your area"

**Troubleshooting Steps:**
1. **Verify service area settings:**
   - Go to Profile > Service Areas
   - Confirm your service areas are correctly set
   - Ensure your account is fully verified

2. **Check lead filters:**
   - Reset any active filters that might be limiting visible leads
   - Verify that your service type selections match available leads

3. **Confirm account status:**
   - Ensure your subscription is active
   - Check for any payment issues that might limit lead access

### Problems Claiming Leads

**Symptoms:**
- "Unable to claim lead" error message
- Payment processing error when attempting to claim

**Troubleshooting Steps:**
1. **Verify payment method:**
   - Check that your default payment method is valid and not expired
   - Ensure you have sufficient funds or credit available
   
2. **Check for lead status changes:**
   - The lead may have been claimed by another plumber
   - Refresh the page to get updated lead availability

3. **Test with a different lead:**
   - If the issue persists with multiple leads, there may be an account problem
   - Contact support if the issue persists

### Missing Lead Information

**Symptoms:**
- Lead details are incomplete after claiming
- Customer contact information is missing

**Troubleshooting Steps:**
1. **Refresh the lead details page:**
   - Sometimes lead details take a moment to fully load
   
2. **Check for browser rendering issues:**
   - Try accessing the lead from a different device
   - Clear your browser cache and reload

3. **Verify payment completion:**
   - Lead details are only fully visible after payment is complete
   - Check your payment history to confirm the transaction

## Payment Problems

### Failed Payments

**Symptoms:**
- "Payment declined" or "Payment failed" error messages
- Unable to claim leads despite having an active payment method

**Troubleshooting Steps:**
1. **Verify payment method details:**
   - Check that your card information is current and correct
   - Ensure the billing address matches your card's registered address
   
2. **Contact your bank:**
   - Your bank may be blocking the transaction as suspicious
   - Ask your bank to allow transactions from "PlumberLeads"
   
3. **Try an alternate payment method:**
   - Add a different card to your account
   - If available, try ACH bank transfer instead

### Missing or Incorrect Charges

**Symptoms:**
- Charges don't appear in your billing history
- Amount charged differs from lead price shown

**Troubleshooting Steps:**
1. **Check transaction timing:**
   - New charges may take up to 24 hours to appear in your billing history
   
2. **Review lead details:**
   - Confirm the original lead price in your claimed leads section
   - Verify if any discounts or promotions were applied

3. **Request transaction details:**
   - Contact support for a detailed breakdown of the transaction
   - Have the lead ID and approximate time of claim ready

### Refund Request Issues

**Symptoms:**
- Unable to submit a refund request
- Refund request showing "Pending" for an extended period

**Troubleshooting Steps:**
1. **Verify eligibility:**
   - Refund requests must be submitted within 24 hours of claiming a lead
   - The lead must meet the refund policy criteria (invalid contact info, etc.)
   
2. **Check submission details:**
   - Ensure all required fields in the refund request form are completed
   - Provide specific details about why the lead qualifies for a refund
   
3. **Follow up with support:**
   - If a request has been pending for more than 48 hours, contact support
   - Reference your refund request ID in communications

## Profile and Account Settings

### Unable to Update Profile

**Symptoms:**
- Changes to profile don't save
- "Error updating profile" message appears

**Troubleshooting Steps:**
1. **Check for validation errors:**
   - Red error messages may indicate specific field issues
   - Ensure all required fields are completed correctly
   
2. **Image upload issues:**
   - Profile images must be under 5MB and in JPG, PNG, or GIF format
   - Try resizing large images before uploading
   
3. **Service area limitations:**
   - There may be a limit on the number of service areas you can select
   - Remove some areas before adding new ones if at the limit

### Changes Not Reflecting

**Symptoms:**
- Profile updates appear to save but don't show up when viewing profile
- Service area changes don't affect available leads

**Troubleshooting Steps:**
1. **Allow for processing time:**
   - Some changes (especially service areas) may take up to 30 minutes to fully process
   
2. **Clear browser cache:**
   - Your browser may be showing cached profile information
   - Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)
   
3. **Try a different browser:**
   - If changes appear in a different browser, clear cache on your primary browser

## Notification Troubleshooting

### Missing Email Notifications

**Symptoms:**
- Not receiving email alerts about new leads
- Missing account notifications or receipts

**Troubleshooting Steps:**
1. **Check notification settings:**
   - Verify email notifications are enabled in Settings > Notifications
   
2. **Review spam/junk folders:**
   - Add noreply@plumberleads.com to your safe senders list
   - Check all email folders including Promotions, Updates, etc.
   
3. **Verify email address:**
   - Ensure your email address is entered correctly in your profile
   - Consider adding an alternate email address if available

### SMS Notification Problems

**Symptoms:**
- Not receiving text message alerts
- Delayed or incomplete SMS notifications

**Troubleshooting Steps:**
1. **Verify phone number:**
   - Check that your mobile number is entered correctly with country code
   - Confirm SMS notifications are enabled in Settings > Notifications
   
2. **Check carrier issues:**
   - Some carriers may block automated messages
   - Reply STOP and then START to 85775 (PlumberLeads SMS code)
   
3. **Device settings:**
   - Ensure your phone is not blocking messages from short codes
   - Check if you've reached any carrier-imposed SMS limits

## Mobile Access Issues

### Display Problems on Mobile

**Symptoms:**
- Interface elements appear cut off or misaligned
- Buttons or forms don't work properly on mobile

**Troubleshooting Steps:**
1. **Try different orientation:**
   - Rotate your device between portrait and landscape
   
2. **Update your browser:**
   - Ensure you're using the latest version of your mobile browser
   - Chrome and Safari provide the best mobile experience
   
3. **Clear browser data:**
   - Clear cache and cookies in your mobile browser
   - Reload the page after clearing data

### Slow Performance on Mobile

**Symptoms:**
- Pages take a long time to load on mobile devices
- Actions like claiming leads are sluggish

**Troubleshooting Steps:**
1. **Check internet connection:**
   - Switch between WiFi and cellular data to identify connection issues
   - Run a speed test to verify adequate bandwidth
   
2. **Close background apps:**
   - Too many active apps can slow down browser performance
   - Restart your phone if performance issues persist
   
3. **Try lite mode:**
   - Enable "Lite" or "Data Saver" mode in your mobile browser
   - This can improve performance on slower connections

## Performance Problems

### Slow Website Response

**Symptoms:**
- Pages take a long time to load
- Actions like searching or filtering are delayed

**Troubleshooting Steps:**
1. **Check your internet connection:**
   - Run a speed test at speedtest.net
   - Try accessing other websites to compare performance
   
2. **Hardware limitations:**
   - Close unused applications and browser tabs
   - Restart your computer if it's been running for extended periods
   
3. **Browser extensions:**
   - Temporarily disable browser extensions, which can slow performance
   - Try incognito/private browsing mode as a test

### Timeouts or Errors During Peak Hours

**Symptoms:**
- "Request timeout" or "Server not responding" errors
- Intermittent failures when performing actions

**Troubleshooting Steps:**
1. **Try again later:**
   - Peak usage times (typically 8-10am and 4-6pm) may cause temporary slowdowns
   
2. **Refresh vs. retry:**
   - Instead of repeatedly clicking buttons, refresh the page and try again
   - Excessive retries can worsen performance issues
   
3. **Check system status:**
   - Visit status.plumberleads.com to check for known system issues
   - Planned maintenance is usually announced in advance

## Error Message Reference

### Common Error Codes

#### Error 1001: Authentication Failed
**Cause:** Invalid credentials or expired session
**Solution:** Re-enter credentials, reset password if necessary

#### Error 1002: Payment Processing Failed
**Cause:** Card declined or payment information issues
**Solution:** Update payment information or contact your bank

#### Error 1003: Lead Unavailable
**Cause:** Lead was claimed by another plumber or expired
**Solution:** Refresh available leads list and select a different lead

#### Error 1004: Profile Update Failed
**Cause:** Invalid input or database constraint violation
**Solution:** Check error details and adjust input accordingly

#### Error 1005: Rate Limit Exceeded
**Cause:** Too many requests in a short time period
**Solution:** Wait 5 minutes before trying again

#### Error 2001: Server Error
**Cause:** Internal system issue
**Solution:** Report to support with the error code and timestamp

## System Status and Maintenance

### Checking System Status

1. **Status Page:**
   - Visit status.plumberleads.com for real-time system status
   - Subscribe to updates for notifications about outages

2. **Scheduled Maintenance:**
   - Maintenance is typically scheduled during off-peak hours (1-4am EST)
   - Notifications are sent 48 hours before scheduled maintenance

3. **Recent Updates:**
   - System updates and new features are announced in the dashboard
   - Release notes are available in the Help section

## Getting Support

### When to Contact Support

Contact support when:
- You've tried the relevant troubleshooting steps without success
- You encounter an error not covered in this guide
- You need assistance with account-specific issues
- You discover what appears to be a bug or system error

### Support Channels

1. **Email Support:**
   - support@plumberleads.com
   - 24-48 hour response time

2. **Phone Support:**
   - (555) 123-4567
   - Available Monday-Friday, 8am-8pm EST
   - Saturday, 9am-5pm EST

3. **Live Chat:**
   - Available on the website during business hours
   - Fastest response for urgent issues

### Information to Provide

When contacting support, please include:
- Your account email address
- Device and browser being used
- Detailed description of the issue
- Steps you've already taken to resolve it
- Screenshots of error messages (if applicable)
- Time and date when the issue occurred

---

This troubleshooting guide is regularly updated. Last update: July 2023. 
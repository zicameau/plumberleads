# app/services/notification_service.py
import os
from flask import current_app, render_template
from flask_mail import Mail, Message
import logging

# Initialize Flask-Mail
mail = Mail()

# Optional: Initialize Twilio for SMS if configured
try:
    from twilio.rest import Client as TwilioClient
    twilio_client = None
except ImportError:
    TwilioClient = None
    twilio_client = None


def init_notification_services(app):
    """Initialize email and SMS services."""
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize Twilio if configured
    global twilio_client
    if TwilioClient and app.config.get('TWILIO_ACCOUNT_SID') and app.config.get('TWILIO_AUTH_TOKEN'):
        twilio_client = TwilioClient(
            app.config['TWILIO_ACCOUNT_SID'],
            app.config['TWILIO_AUTH_TOKEN']
        )


def send_email(recipient, subject, template, **context):
    """
    Send an email using Flask-Mail.
    
    Args:
        recipient: Email address of the recipient
        subject: Email subject
        template: Jinja2 template name
        **context: Template context variables
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Render template
        html_body = render_template(f"emails/{template}.html", **context)
        text_body = render_template(f"emails/{template}.txt", **context)
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=text_body,
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Send email
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False


def send_sms(phone_number, message):
    """
    Send an SMS using Twilio.
    
    Args:
        phone_number: Recipient's phone number
        message: SMS content
    
    Returns:
        True if SMS sent successfully, False otherwise
    """
    if not twilio_client:
        current_app.logger.warning("Twilio client not configured, SMS not sent")
        return False
        
    try:
        # Format phone number if needed
        if not phone_number.startswith('+'):
            # Default to US if no country code
            phone_number = f"+1{phone_number}"
        
        # Send SMS
        twilio_client.messages.create(
            body=message,
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=phone_number
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending SMS: {str(e)}")
        return False


def send_customer_confirmation(lead):
    """
    Send a confirmation email and optional SMS to the customer.
    
    Args:
        lead: Lead object with customer information
    
    Returns:
        True if at least one notification sent successfully
    """
    # Send confirmation email
    email_sent = send_email(
        recipient=lead.email,
        subject="Your Plumbing Service Request Has Been Received",
        template="customer_confirmation",
        lead=lead,
        app_name=current_app.config.get('APP_NAME', 'Plumber Leads')
    )
    
    # Send SMS if phone number is available
    sms_sent = False
    if lead.phone:
        sms_message = (
            f"Thank you for your plumbing service request. "
            f"We're matching you with plumbers in your area. "
            f"You'll be contacted shortly."
        )
        sms_sent = send_sms(lead.phone, sms_message)
    
    return email_sent or sms_sent


def send_plumber_notification(plumber, lead):
    """
    Send a notification about a new lead to a plumber.
    
    Args:
        plumber: Plumber object
        lead: Lead object
    
    Returns:
        True if at least one notification sent successfully
    """
    # Send email notification
    email_sent = send_email(
        recipient=plumber.email,
        subject="New Plumbing Service Lead Available",
        template="plumber_lead_notification",
        plumber=plumber,
        lead=lead,
        lead_price=current_app.config.get('LEAD_PRICE', 10.00),
        app_name=current_app.config.get('APP_NAME', 'Plumber Leads')
    )
    
    # Send SMS if phone number is available
    sms_sent = False
    if plumber.phone:
        sms_message = (
            f"New plumbing lead available in {lead.city}, {lead.state}. "
            f"Service needed: {lead.service_needed}. "
            f"Log in to view details and claim this lead."
        )
        sms_sent = send_sms(plumber.phone, sms_message)
    
    return email_sent or sms_sent


def send_lead_claimed_notification(lead, plumber, customer_message=None):
    """
    Send a notification when a lead is claimed by a plumber.
    
    Args:
        lead: Lead object
        plumber: Plumber who claimed the lead
        customer_message: Optional custom message from plumber to customer
    
    Returns:
        True if notification sent successfully
    """
    # Send email to customer
    email_context = {
        'lead': lead,
        'plumber': plumber,
        'customer_message': customer_message,
        'app_name': current_app.config.get('APP_NAME', 'Plumber Leads')
    }
    
    email_sent = send_email(
        recipient=lead.email,
        subject=f"{plumber.company_name} will be contacting you about your plumbing request",
        template="lead_claimed_notification",
        **email_context
    )
    
    # Send SMS if phone number is available
    sms_sent = False
    if lead.phone:
        sms_message = (
            f"{plumber.company_name} will be contacting you about your plumbing request. "
            f"Contact: {plumber.phone}"
        )
        if customer_message:
            sms_message += f" Message: {customer_message[:100]}"
            
        sms_sent = send_sms(lead.phone, sms_message)
    
    return email_sent or sms_sent


def send_subscription_confirmation(plumber, subscription):
    """
    Send a confirmation when a plumber subscribes to the service.
    
    Args:
        plumber: Plumber object
        subscription: Stripe subscription object
    
    Returns:
        True if notification sent successfully
    """
    email_sent = send_email(
        recipient=plumber.email,
        subject="Your Plumber Leads Subscription is Active",
        template="subscription_confirmation",
        plumber=plumber,
        subscription=subscription,
        app_name=current_app.config.get('APP_NAME', 'Plumber Leads')
    )
    
    # Send SMS if phone number is available
    sms_sent = False
    if plumber.phone:
        sms_message = (
            f"Your Plumber Leads subscription is now active. "
            f"You can now receive and claim leads in your area."
        )
        sms_sent = send_sms(plumber.phone, sms_message)
    
    return email_sent or sms_sent


def send_lead_credit_purchase_confirmation(plumber, credit_count, amount):
    """
    Send a confirmation when a plumber purchases lead credits.
    
    Args:
        plumber: Plumber object
        credit_count: Number of credits purchased
        amount: Amount paid in dollars
    
    Returns:
        True if notification sent successfully
    """
    email_sent = send_email(
        recipient=plumber.email,
        subject=f"You've Purchased {credit_count} Lead Credits",
        template="lead_credit_purchase",
        plumber=plumber,
        credit_count=credit_count,
        amount=amount,
        new_balance=plumber.lead_credits,
        app_name=current_app.config.get('APP_NAME', 'Plumber Leads')
    )
    
    return email_sent

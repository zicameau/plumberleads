# app/services/payment_service.py
import stripe
from flask import current_app
from datetime import datetime

# Global Stripe API client
_stripe = None

def init_stripe(api_key):
    """Initialize the Stripe client with the provided API key."""
    global _stripe
    stripe.api_key = api_key
    _stripe = stripe
    return _stripe

def get_stripe():
    """Get the initialized Stripe client."""
    global _stripe
    if _stripe is None:
        api_key = current_app.config['STRIPE_API_KEY']
        _stripe = stripe
        stripe.api_key = api_key
    return _stripe

def create_customer(email, name, metadata=None):
    """
    Create a new Stripe customer.
    
    Args:
        email: Customer's email address
        name: Customer's name
        metadata: Additional metadata (dict)
    
    Returns:
        Stripe customer object if successful, None otherwise
    """
    stripe_client = get_stripe()
    try:
        customer = stripe_client.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {}
        )
        return customer
    except Exception as e:
        current_app.logger.error(f"Error creating Stripe customer: {str(e)}")
        return None

def create_subscription(customer_id, price_id, metadata=None):
    """
    Create a new Stripe subscription.
    
    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID for the subscription
        metadata: Additional metadata (dict)
    
    Returns:
        Stripe subscription object if successful, None otherwise
    """
    stripe_client = get_stripe()
    try:
        subscription = stripe_client.Subscription.create(
            customer=customer_id,
            items=[{'price': price_id}],
            payment_behavior='default_incomplete',
            payment_settings={'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
            metadata=metadata or {}
        )
        return subscription
    except Exception as e:
        current_app.logger.error(f"Error creating Stripe subscription: {str(e)}")
        return None

def cancel_subscription(subscription_id):
    """
    Cancel a Stripe subscription.
    
    Args:
        subscription_id: Stripe subscription ID
    
    Returns:
        Cancelled subscription object if successful, None otherwise
    """
    stripe_client = get_stripe()
    try:
        subscription = stripe_client.Subscription.delete(subscription_id)
        return subscription
    except Exception as e:
        current_app.logger.error(f"Error cancelling subscription: {str(e)}")
        return None

def update_subscription(subscription_id, price_id=None, metadata=None):
    """
    Update a Stripe subscription.
    
    Args:
        subscription_id: Stripe subscription ID
        price_id: New Stripe price ID (optional)
        metadata: Additional metadata to update (dict, optional)
    
    Returns:
        Updated subscription object if successful, None otherwise
    """
    stripe_client = get_stripe()
    try:
        update_params = {}
        
        if price_id:
            # Get the current subscription to find the item ID
            subscription = stripe_client.Subscription.retrieve(subscription_id)
            if subscription.items.data:
                item_id = subscription.items.data[0].id
                update_params['items'] = [{'id': item_id, 'price': price_id}]
        
        if metadata:
            update_params['metadata'] = metadata
            
        if update_params:
            subscription = stripe_client.Subscription.modify(
                subscription_id,
                **update_params
            )
            return subscription
        return None
    except Exception as e:
        current_app.logger.error(f"Error updating subscription: {str(e)}")
        return None

def create_checkout_session(customer_id, price_id, success_url, cancel_url, metadata=None):
    """
    Create a Stripe Checkout session for a subscription.
    
    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID
        success_url: URL to redirect upon successful payment
        cancel_url: URL to redirect if payment is cancelled
        metadata: Additional metadata (dict)
    
    Returns:
        Checkout session object if successful, None otherwise
    """
    stripe_client = get_stripe()
    try:
        checkout_session = stripe_client.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {}
        )
        return checkout_session
    except Exception as e:
        current_app.logger.error(f"Error creating checkout session: {str(e)}")
        return None

def create_lead_payment_intent(customer_id, amount, metadata=None):
    """
    Create a payment intent for purchasing lead credits.
    
    Args:
        customer_id: Stripe customer ID
        amount: Amount in cents (integer)
        metadata: Additional metadata (dict)
    
    Returns:
        Payment intent object if successful, None otherwise
    """
    stripe_client = get_stripe()
    try:
        payment_intent = stripe_client.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=customer_id,
            metadata=metadata or {}
        )
        return payment_intent
    except Exception as e:
        current_app.logger.error(f"Error creating payment intent: {str(e)}")
        return None

def verify_webhook_signature(payload, sig_header, webhook_secret=None):
    """
    Verify that a webhook came from Stripe.
    
    Args:
        payload: Request body (bytes)
        sig_header: Stripe-Signature header
        webhook_secret: Webhook signing secret (optional)
    
    Returns:
        The event if signature verification is successful, None otherwise
    """
    stripe_client = get_stripe()
    
    if webhook_secret is None:
        webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']
        
    try:
        event = stripe_client.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        return event
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"Invalid webhook signature: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Error verifying webhook: {str(e)}")
        return None

def get_payment_methods(customer_id, type='card'):
    """
    Get a customer's saved payment methods.
    
    Args:
        customer_id: Stripe customer ID
        type: Payment method type (default: 'card')
    
    Returns:
        List of payment methods if successful, empty list otherwise
    """
    stripe_client = get_stripe()
    try:
        payment_methods = stripe_client.PaymentMethod.list(
            customer=customer_id,
            type=type
        )
        return payment_methods.data
    except Exception as e:
        current_app.logger.error(f"Error retrieving payment methods: {str(e)}")
        return []

def get_invoice(invoice_id):
    """
    Get a specific invoice.
    
    Args:
        invoice_id: Stripe invoice ID
    
    Returns:
        Invoice object if successful, None otherwise
    """
    stripe_client = get_stripe()
    try:
        invoice = stripe_client.Invoice.retrieve(invoice_id)
        return invoice
    except Exception as e:
        current_app.logger.error(f"Error retrieving invoice: {str(e)}")
        return None
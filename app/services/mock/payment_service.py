"""Mock payment service for testing."""

def init_stripe(api_key):
    """Initialize Stripe with the given API key."""
    print(f"Mock: Initializing Stripe with API key: {api_key[:4]}...")
    return True

def create_customer(email, name=None, metadata=None):
    """Create a Stripe customer."""
    print(f"Mock: Creating customer for {email}")
    return {"id": "cus_mock_123456"}

def create_subscription(customer_id, price_id):
    """Create a subscription for a customer."""
    print(f"Mock: Creating subscription for customer {customer_id} with price {price_id}")
    return {"id": "sub_mock_123456", "status": "active"}

def create_checkout_session(customer_id, price_id, success_url, cancel_url):
    """Create a checkout session for a subscription."""
    print(f"Mock: Creating checkout session for customer {customer_id}")
    return {"id": "cs_mock_123456", "url": "https://example.com/checkout"}

def create_lead_payment_intent(amount, customer_id, metadata=None):
    """Create a payment intent for a lead."""
    print(f"Mock: Creating payment intent for ${amount} from customer {customer_id}")
    return {"id": "pi_mock_123456", "client_secret": "pi_mock_secret_123456"}

def get_payment_methods(customer_id):
    """Get payment methods for a customer."""
    print(f"Mock: Getting payment methods for customer {customer_id}")
    return [{"id": "pm_mock_123456", "card": {"brand": "visa", "last4": "4242"}}] 
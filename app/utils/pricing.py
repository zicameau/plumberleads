from flask import current_app

def calculate_lead_price(job_price):
    """
    Calculate the price a plumber needs to pay to claim a lead.
    Uses the configured percentage of the job price with a minimum price floor.
    
    Args:
        job_price (float): The total price of the job/project
        
    Returns:
        dict: Contains both the calculated lead price and the calculation details
            {
                'lead_price': float,  # The final price to charge
                'calculated_price': float,  # Price before minimum check
                'minimum_price': float,  # Minimum price threshold
                'percentage': float,  # Percentage used for calculation
                'is_minimum_price': bool  # Whether minimum price was used
            }
    """
    # Get configuration values with defaults
    percentage = current_app.config.get('LEAD_CLAIM_PERCENTAGE', 0.15)
    minimum_price = current_app.config.get('MINIMUM_LEAD_PRICE', 30.00)
    
    # Calculate price based on percentage
    calculated_price = job_price * percentage
    
    # Use the higher of calculated price or minimum price
    final_price = max(calculated_price, minimum_price)
    
    return {
        'lead_price': final_price,
        'calculated_price': calculated_price,
        'minimum_price': minimum_price,
        'percentage': percentage,
        'is_minimum_price': calculated_price < minimum_price
    } 
from supabase import create_client, Client
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """Get or create a Supabase client instance."""
    try:
        url = current_app.config['SUPABASE_URL']
        key = current_app.config['SUPABASE_KEY']
        
        if not url or not key:
            raise ValueError("Supabase URL and key must be configured")
            
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise 
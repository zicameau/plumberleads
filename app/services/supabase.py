from supabase import create_client, Client
from app.services.mock.supabase_mock import SupabaseMock

class SupabaseClient:
    _instance = None
    _client = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = None
    
    def set_client(self, client):
        """Set the Supabase client (used for testing)."""
        self._client = client
    
    def get_client(self) -> Client:
        """Get the Supabase client instance."""
        if self._client is None:
            raise RuntimeError("Supabase client not initialized. Call init_supabase first.")
        return self._client

def init_supabase(url: str, key: str, testing: bool = False):
    """Initialize the Supabase client."""
    if testing:
        # Use mock client for testing
        mock_client = SupabaseMock()
        SupabaseClient.get_instance().set_client(mock_client)
    else:
        # Create real Supabase client
        client = create_client(url, key)
        SupabaseClient.get_instance().set_client(client)

def get_supabase() -> Client:
    """Get the Supabase client instance."""
    return SupabaseClient.get_instance().get_client() 
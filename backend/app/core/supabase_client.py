"""
Supabase client initialization and management.

Provides singleton instances of the Supabase client for both
anonymous (user-level) and service-role (admin-level) operations.
"""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Return a cached Supabase client using the anonymous key.
    
    This client respects Row Level Security (RLS) policies and should
    be used for user-facing operations where the JWT token is passed.
    """
    settings = get_settings()
    client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return client


@lru_cache()
def get_supabase_admin() -> Client:
    """
    Return a cached Supabase client using the service role key.
    
    This client bypasses Row Level Security (RLS) and should only be
    used for admin operations, background tasks, and server-side logic
    that needs unrestricted database access.
    """
    settings = get_settings()
    client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return client

from supabase import create_client, Client
from .settings import settings    

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_PUBLISHABLE_KEY
)

supabase_admin: Client | None = None

if settings.SUPABASE_SECRET_KEY:
    supabase_admin = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SECRET_KEY
    )

def get_supabase():
    return supabase

def get_supabase_admin():
    if not supabase_admin:
        raise RuntimeError("Secret key not configured.")
    return supabase_admin

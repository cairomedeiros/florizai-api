from ..config.redis_client import get_redis_client

def invalidate_cache(user_id: str):
    client = get_redis_client()
    cache_key = f"plants_user_{user_id}"
    client.delete(cache_key)
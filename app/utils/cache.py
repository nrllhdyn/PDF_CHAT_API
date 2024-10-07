from cachetools import TTLCache, cached

# Create a cache with a time-to-live of 600 seconds and a maximum size of 100 items
cache = TTLCache(maxsize=100, ttl=600)

def cache_key(pdf_id: str, question: str) -> str:
    return f"{pdf_id}:{question}"

@cached(cache, key=cache_key)
def get_cached_response(pdf_id: str, question: str) -> str:
    return None

def set_cached_response(pdf_id: str, question: str, response: str):
    cache[cache_key(pdf_id, question)] = response
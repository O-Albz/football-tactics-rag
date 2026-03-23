import json
import hashlib
from pathlib import Path

CACHE_PATH = Path("cache/queries.json")

def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    with open(CACHE_PATH) as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def _save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

def _cache_key(question: str, top_k: int) -> str:
    raw = f"{question.strip().lower()}|{top_k}"
    return hashlib.md5(raw.encode()).hexdigest()

def get_cached(question: str, top_k: int) -> dict | None:
    cache = _load_cache()
    key = _cache_key(question, top_k)
    return cache.get(key)

def set_cached(question: str, top_k: int, result: dict):
    cache = _load_cache()
    key = _cache_key(question, top_k)
    cache[key] = result
    _save_cache(cache)
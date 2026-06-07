"""
backend/src/services/cache_service.py

Video Scan Cache Service
------------------------
Stores scan results on disk using SHA-256 hash of the YouTube URL as key.
Same URL = instant result from cache, no re-processing needed.

Cache location:  backend/cache/  (auto-created)
Cache format:    JSON files  ->  {url_hash}.json
Cache expiry:    Configurable via .env  CACHE_EXPIRY_DAYS  (default: 7 days)
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger("national-security-guardian")

# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------

# Yeh path automatically  backend/cache/  folder banata hai
CACHE_DIR = os.path.join(
    os.path.dirname(__file__),   # services/
    "..",                         # src/
    "..",                         # backend/
    "cache"                       # backend/cache/
)

CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "7"))


# ---------------------------------------------------------------
# PRIVATE HELPERS
# ---------------------------------------------------------------

def _ensure_cache_dir():
    """cache/ folder banao agar exist nahi karta."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def _url_to_key(video_url: str) -> str:
    """
    YouTube URL ko ek unique 16-char cache key mein convert karo.
    Yeh sab ek hi key par map honge:
      https://youtube.com/watch?v=abc123
      https://youtu.be/abc123
      https://youtube.com/watch?v=abc123&t=30s
    """
    url_clean = video_url.strip().lower()

    # youtu.be short link handle karo
    if "youtu.be/" in url_clean:
        vid_id = url_clean.split("youtu.be/")[-1].split("?")[0].split("&")[0]
    elif "v=" in url_clean:
        vid_id = url_clean.split("v=")[-1].split("&")[0].split("#")[0]
    else:
        vid_id = url_clean  # fallback: full URL hash

    return hashlib.sha256(vid_id.encode()).hexdigest()[:16]


def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")


# ---------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------

def get_cached_result(video_url: str) -> Optional[Dict[str, Any]]:
    """
    Is URL ke liye cached result check karo.

    Returns:
        Dict  -> cache hit mila aur expire nahi hua
        None  -> cache miss ya expire ho gaya
    """
    _ensure_cache_dir()
    key  = _url_to_key(video_url)
    path = _cache_path(key)

    if not os.path.exists(path):
        logger.info(f"[Cache] MISS — no cached result for: {video_url[:60]}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            cached = json.load(f)

        # Expiry check
        cached_at = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
        age       = datetime.utcnow() - cached_at

        if age > timedelta(days=CACHE_EXPIRY_DAYS):
            logger.info(f"[Cache] EXPIRED — {age.days}d old (limit {CACHE_EXPIRY_DAYS}d): {video_url[:60]}")
            os.remove(path)
            return None

        age_display = f"{age.seconds // 3600}h" if age.days == 0 else f"{age.days}d"
        logger.info(f"[Cache] HIT — returning cached result ({age_display} ago): {video_url[:60]}")
        return cached.get("result")

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning(f"[Cache] Corrupt file {path} — deleting. Error: {e}")
        os.remove(path)
        return None


def save_to_cache(video_url: str, result: Dict[str, Any]) -> bool:
    """
    Scan result ko cache mein save karo.

    Args:
        video_url : jo YouTube URL scan hua
        result    : LangGraph final_state ka dict

    Returns:
        True on success, False on failure
    """
    _ensure_cache_dir()
    key  = _url_to_key(video_url)
    path = _cache_path(key)

    try:
        cache_entry = {
            "video_url":  video_url,
            "cached_at":  datetime.utcnow().isoformat(),
            "expires_in": f"{CACHE_EXPIRY_DAYS} days",
            "result":     result
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache_entry, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"[Cache] SAVED — key={key}: {video_url[:60]}")
        return True

    except Exception as e:
        logger.error(f"[Cache] Failed to save: {e}")
        return False


def invalidate_cache(video_url: str) -> bool:
    """
    Ek specific URL ka cache delete karo.
    Iske baad woh URL dobara full pipeline se scan hoga.
    """
    key  = _url_to_key(video_url)
    path = _cache_path(key)

    if os.path.exists(path):
        os.remove(path)
        logger.info(f"[Cache] INVALIDATED — key={key}: {video_url[:60]}")
        return True

    logger.info(f"[Cache] Nothing to invalidate for: {video_url[:60]}")
    return False


def list_cache() -> list:
    """
    Saare cached entries ki list do with metadata.
    /cache GET endpoint ke liye use hota hai.
    """
    _ensure_cache_dir()
    entries = []

    for filename in os.listdir(CACHE_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(CACHE_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
            age_hours = int((datetime.utcnow() - cached_at).total_seconds() // 3600)

            entries.append({
                "key":       filename.replace(".json", ""),
                "video_url": data.get("video_url", "unknown"),
                "status":    data.get("result", {}).get("final_status", "?"),
                "cached_at": data.get("cached_at"),
                "age_hours": age_hours,
            })
        except Exception:
            continue

    return sorted(entries, key=lambda x: x.get("cached_at", ""), reverse=True)


def clear_all_cache() -> int:
    """Saara cache delete karo. Returns: kitni files delete hui."""
    _ensure_cache_dir()
    count = 0
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, filename))
            count += 1
    logger.info(f"[Cache] Cleared {count} entries.")
    return count
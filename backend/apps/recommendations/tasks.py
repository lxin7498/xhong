"""Async recommendation computation using a background thread pool.

This avoids blocking the HTTP request cycle when the rating matrix
grows large.  The view returns cached results immediately while a
background worker recomputes fresh recommendations.

For a production deployment at scale you would replace this with
Celery + Redis, but the interface (submit task → poll status →
read result) stays the same.
"""

from concurrent.futures import ThreadPoolExecutor, Future
from django.core.cache import cache

from apps.recommendations.engine import compute_recommendations

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="recs")

STATUS_KEY = "recs:status:{user_id}"
RESULT_KEY = "recs:{user_id}"


def _run_and_cache(user_id):
    """Compute recommendations for *user_id* and store in cache."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        cache.set(STATUS_KEY.format(user_id=user_id), "error", 600)
        return
    result = compute_recommendations(user)
    cache.set(RESULT_KEY.format(user_id=user_id), result, 3600)
    cache.set(STATUS_KEY.format(user_id=user_id), "ready", 3600)


def schedule_compute(user_id: int) -> Future:
    """Kick off an async recommendation compute for *user_id*.

    Returns the Future so callers can optionally wait, but the
    standard flow is fire-and-forget.
    """
    # Mark as computing so the frontend can show a spinner
    cache.set(STATUS_KEY.format(user_id=user_id), "computing", 120)
    return _executor.submit(_run_and_cache, user_id)


def get_status(user_id: int) -> str | None:
    """Return 'computing', 'ready', 'error', or None (never computed)."""
    return cache.get(STATUS_KEY.format(user_id=user_id))

"""
Job Runner — Phase 2
Singleton ThreadPoolExecutor for background media processing.
No Redis, no Celery — single-user app doesn't need them.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

# 2 workers: one converts images, one handles ZIPs concurrently
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="gallery_worker")


def submit(fn: Callable, *args: Any, **kwargs: Any):
    """
    Submit a function to run in the background thread pool.
    Returns a Future (can be ignored for fire-and-forget tasks).
    """
    return _executor.submit(fn, *args, **kwargs)


def shutdown(wait: bool = True) -> None:
    """Graceful shutdown (called on app exit)."""
    _executor.shutdown(wait=wait)

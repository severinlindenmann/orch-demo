"""Small shared helpers that don't deserve their own module yet."""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Testable wrapper around `datetime.now(timezone.utc)`."""
    return datetime.now(timezone.utc)


def chunk(items: list, size: int) -> list[list]:
    """Split `items` into consecutive chunks of at most `size` elements."""
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i : i + size] for i in range(0, len(items), size)]

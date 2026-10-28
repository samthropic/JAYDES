"""
In-memory cache for query results.
"""
import copy


_store = {}


def get(key):
    """Return a copy of the cached value, or None if key is absent."""
    if key not in _store:
        return None
    return copy.deepcopy(_store[key])


def put(key, value):
    """Store a copy of value under key."""
    _store[key] = copy.deepcopy(value)


def invalidate(key):
    """Drop one cached value."""
    _store.pop(key, None)

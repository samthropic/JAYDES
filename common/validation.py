"""Shared primitive validation helpers."""
import math


def is_integer(value):
    """Return whether value is an integer, excluding booleans."""
    return isinstance(value, int) and not isinstance(value, bool)


def is_finite_number(value):
    """Return whether value is a finite integer or float, excluding bools."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and (not isinstance(value, float) or math.isfinite(value))
    )

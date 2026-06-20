from __future__ import annotations

import math

_SQRT_TWO = math.sqrt(2.0)
_INV_SQRT_TWO_PI = 1.0 / math.sqrt(2.0 * math.pi)


def standard_normal_cdf(value: float) -> float:
    """Return the standard normal cumulative distribution function."""
    return 0.5 * math.erfc(-value / _SQRT_TWO)


def standard_normal_pdf(value: float) -> float:
    """Return the standard normal probability density function."""
    return _INV_SQRT_TWO_PI * math.exp(-0.5 * value * value)

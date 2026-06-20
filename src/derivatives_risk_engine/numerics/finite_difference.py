from __future__ import annotations

from collections.abc import Callable

from derivatives_risk_engine.core.validation import require_finite, require_positive


def central_difference(function: Callable[[float], float], point: float, bump: float) -> float:
    """Approximate the first derivative with an absolute central bump.

    Args:
        function: Scalar deterministic function to differentiate.
        point: Input value where the derivative is evaluated.
        bump: Strictly positive absolute bump in the same units as ``point``.
    """
    require_finite("point", point)
    require_positive("bump", bump)
    return (function(point + bump) - function(point - bump)) / (2.0 * bump)


def second_order_central_difference(
    function: Callable[[float], float],
    point: float,
    bump: float,
) -> float:
    """Approximate the second derivative with an absolute central bump.

    Args:
        function: Scalar deterministic function to differentiate.
        point: Input value where the second derivative is evaluated.
        bump: Strictly positive absolute bump in the same units as ``point``.
    """
    require_finite("point", point)
    require_positive("bump", bump)
    return (function(point + bump) - 2.0 * function(point) + function(point - bump)) / (bump * bump)

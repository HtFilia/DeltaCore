from math import isfinite

from derivatives_risk_engine.core.exceptions import DomainInputError


def require_finite(name: str, value: float) -> None:
    """Require a finite numeric input."""
    if not isfinite(value):
        raise DomainInputError(f"{name} must be finite")


def require_positive(name: str, value: float) -> None:
    """Require a strictly positive numeric input."""
    require_finite(name, value)
    if value <= 0.0:
        raise DomainInputError(f"{name} must be greater than zero")


def require_non_negative(name: str, value: float) -> None:
    """Require a non-negative numeric input."""
    require_finite(name, value)
    if value < 0.0:
        raise DomainInputError(f"{name} must be non-negative")

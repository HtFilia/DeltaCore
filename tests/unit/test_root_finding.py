import math

import pytest

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.numerics.root_finding import brent_root


def test_brent_root_converges_with_diagnostics() -> None:
    result = brent_root(
        lambda value: value * value - 2.0,
        lower_bound=0.0,
        upper_bound=2.0,
        absolute_tolerance=1e-12,
    )

    assert result.converged is True
    assert result.root == pytest.approx(math.sqrt(2.0), abs=1e-12)
    assert result.objective_value <= 1e-12
    assert result.iterations > 0
    assert result.lower_bound == 0.0
    assert result.upper_bound == 2.0
    assert result.failure_reason is None


def test_brent_root_returns_structured_failure_when_root_is_not_bracketed() -> None:
    result = brent_root(
        lambda value: value * value + 1.0,
        lower_bound=-1.0,
        upper_bound=1.0,
    )

    assert result.converged is False
    assert result.root is None
    assert result.objective_value == pytest.approx(2.0, abs=1e-12)
    assert result.iterations == 0
    assert result.failure_reason == "root is not bracketed by the supplied bounds"


def test_brent_root_rejects_invalid_bounds() -> None:
    with pytest.raises(DomainInputError, match="lower_bound must be less than upper_bound"):
        brent_root(lambda value: value, lower_bound=1.0, upper_bound=1.0)

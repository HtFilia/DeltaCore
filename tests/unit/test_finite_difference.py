import pytest

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.numerics.finite_difference import (
    central_difference,
    second_order_central_difference,
)


def test_central_difference_approximates_first_derivative() -> None:
    derivative = central_difference(lambda value: value**3, point=2.0, bump=1e-5)

    assert derivative == pytest.approx(12.0, rel=1e-10)


def test_second_order_central_difference_approximates_second_derivative() -> None:
    second_derivative = second_order_central_difference(
        lambda value: value**3,
        point=2.0,
        bump=1e-3,
    )

    assert second_derivative == pytest.approx(12.0, rel=1e-9)


def test_finite_difference_rejects_non_positive_bump() -> None:
    with pytest.raises(DomainInputError, match="bump must be greater than zero"):
        central_difference(lambda value: value, point=1.0, bump=0.0)

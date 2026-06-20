import math

import pytest

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.risk.var import historical_var_expected_shortfall


def test_historical_var_expected_shortfall_uses_loss_quantile_and_tail_mean() -> None:
    pnls = (12.0, 7.0, 5.0, 2.0, 0.0, -1.0, -3.0, -8.0, -10.0, -20.0)

    result = historical_var_expected_shortfall(pnls, confidence_level=0.80)

    assert result.method == "historical"
    assert result.confidence_level == 0.80
    assert result.num_observations == 10
    assert result.quantile_index == 7
    assert result.tail_observations == 3
    assert result.value_at_risk == pytest.approx(8.0, abs=1e-12)
    assert result.expected_shortfall == pytest.approx((8.0 + 10.0 + 20.0) / 3.0, abs=1e-12)


def test_historical_var_expected_shortfall_is_order_independent() -> None:
    pnls = (-20.0, 12.0, -3.0, 5.0, -10.0, 2.0, -8.0, 7.0, -1.0, 0.0)

    result = historical_var_expected_shortfall(pnls, confidence_level=0.80)

    assert result.value_at_risk == pytest.approx(8.0, abs=1e-12)
    assert result.expected_shortfall == pytest.approx((8.0 + 10.0 + 20.0) / 3.0, abs=1e-12)


def test_historical_var_expected_shortfall_handles_flat_pnl_distribution() -> None:
    result = historical_var_expected_shortfall((0.0, 0.0, 0.0, 0.0), confidence_level=0.95)

    assert result.value_at_risk == pytest.approx(0.0, abs=1e-12)
    assert result.expected_shortfall == pytest.approx(0.0, abs=1e-12)
    assert result.tail_observations == 1


def test_historical_var_expected_shortfall_rejects_invalid_confidence_level() -> None:
    with pytest.raises(DomainInputError, match="confidence_level must be between 0 and 1"):
        historical_var_expected_shortfall((1.0, -1.0), confidence_level=1.0)


def test_historical_var_expected_shortfall_rejects_too_few_observations() -> None:
    with pytest.raises(DomainInputError, match="pnls must contain at least 2 observations"):
        historical_var_expected_shortfall((1.0,), confidence_level=0.95)


def test_historical_var_expected_shortfall_rejects_non_finite_pnl() -> None:
    with pytest.raises(DomainInputError, match=r"pnls\[1\] must be finite"):
        historical_var_expected_shortfall((1.0, math.nan), confidence_level=0.95)

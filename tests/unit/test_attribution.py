"""Attribution checks: reference Greeks, signed time and local error behavior."""

from dataclasses import replace

import pytest

from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.risk.attribution import AttributionShock, attribute_scenario

OPTION = EuropeanOption(option_type="call", strike=100, time_to_expiry=1)
MARKET = BlackScholesMarket(spot=100, risk_free_rate=0.05, dividend_yield=0, volatility=0.2)


def test_zero_and_reference_contributions() -> None:
    zero = attribute_scenario(OPTION, MARKET, AttributionShock())
    assert zero.full_pnl == zero.approximation == zero.residual == 0
    result = attribute_scenario(
        OPTION, MARKET, AttributionShock(spot_shift=-5, volatility_shift=0.05)
    )
    assert result.base_price == pytest.approx(10.450583572185565, abs=1e-12)
    assert result.spot_delta == pytest.approx(-5 * 0.6368306511756191, abs=1e-12)
    assert result.spot_gamma == pytest.approx(12.5 * 0.018762017345846895, abs=1e-12)
    assert result.vol_vega == pytest.approx(0.05 * 37.52403469169379, abs=1e-12)
    assert result.full_pnl == pytest.approx(result.approximation + result.residual, abs=1e-12)


@pytest.mark.parametrize("kind", ["call", "put"])
def test_small_shock_residual_and_signed_calendar_decay(kind: str) -> None:
    option = replace(OPTION, option_type=kind)  # type: ignore[arg-type]
    market = replace(MARKET, dividend_yield=0.01)
    small = attribute_scenario(option, market, AttributionShock(spot_shift=0.01))
    large = attribute_scenario(option, market, AttributionShock(spot_shift=10))
    assert abs(small.residual) < 1e-8
    assert abs(large.residual) > abs(small.residual)
    time = attribute_scenario(option, market, AttributionShock(elapsed_years=1e-5))
    assert time.calendar_theta < 0
    assert time.full_pnl == pytest.approx(time.calendar_theta, abs=1e-8)


@pytest.mark.parametrize(
    "shock",
    [
        AttributionShock(spot_shift=-100),
        AttributionShock(volatility_shift=-0.2),
        AttributionShock(elapsed_years=2),
    ],
)
def test_invalid_shocks_rejected(shock: AttributionShock) -> None:
    with pytest.raises(ValueError):
        attribute_scenario(OPTION, MARKET, shock)


def test_positive_base_required_but_shocked_expiry_supported() -> None:
    result = attribute_scenario(OPTION, MARKET, AttributionShock(elapsed_years=1))
    assert result.shocked_price == 0
    assert result.shocked_time_to_expiry == 0
    assert result.limitations
    with pytest.raises(ValueError, match="base expiry"):
        attribute_scenario(replace(OPTION, time_to_expiry=0), MARKET, AttributionShock())

from dataclasses import replace

import pytest

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.models.black_scholes import black_scholes_price
from derivatives_risk_engine.risk.scenario import (
    MarketShock,
    price_black_scholes_scenario,
    run_black_scholes_scenarios,
)


def test_zero_market_shock_has_zero_pnl() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    result = price_black_scholes_scenario(option, market, MarketShock(name="base"))

    assert result.model == "black_scholes"
    assert result.scenario_name == "base"
    assert result.base_price == pytest.approx(black_scholes_price(option, market), abs=1e-12)
    assert result.shocked_price == pytest.approx(result.base_price, abs=1e-12)
    assert result.pnl == pytest.approx(0.0, abs=1e-12)


def test_spot_up_scenario_has_positive_call_pnl() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )
    shock = MarketShock(name="spot_up_5", spot_shift=5.0)

    result = price_black_scholes_scenario(option, market, shock)
    expected_shocked_price = black_scholes_price(option, replace(market, spot=105.0))

    assert result.shock == shock
    assert result.shocked_spot == 105.0
    assert result.shocked_price == pytest.approx(expected_shocked_price, abs=1e-12)
    assert result.pnl > 0.0


def test_volatility_up_scenario_has_positive_option_pnl() -> None:
    option = EuropeanOption(option_type="put", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    result = price_black_scholes_scenario(
        option,
        market,
        MarketShock(name="vol_up_5_points", volatility_shift=0.05),
    )

    assert result.shocked_volatility == pytest.approx(0.25, abs=1e-12)
    assert result.pnl > 0.0


def test_time_decay_scenario_reprices_with_lower_time_to_expiry() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.0,
        dividend_yield=0.0,
        volatility=0.20,
    )

    result = price_black_scholes_scenario(
        option,
        market,
        MarketShock(name="advance_three_months", time_shift=-0.25),
    )
    shocked_option = replace(option, time_to_expiry=0.75)

    assert result.shocked_time_to_expiry == pytest.approx(0.75, abs=1e-12)
    assert result.shocked_price == pytest.approx(
        black_scholes_price(shocked_option, market),
        abs=1e-12,
    )
    assert result.pnl < 0.0


def test_batch_scenarios_preserve_order() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )
    shocks = (
        MarketShock(name="spot_down", spot_shift=-5.0),
        MarketShock(name="rate_up", risk_free_rate_shift=0.01),
    )

    results = run_black_scholes_scenarios(option, market, shocks)

    assert tuple(result.scenario_name for result in results) == ("spot_down", "rate_up")
    assert results[0].pnl < 0.0
    assert results[1].pnl > 0.0


def test_scenario_rejects_invalid_shocked_market_inputs() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    with pytest.raises(DomainInputError, match="shocked spot must be greater than zero"):
        price_black_scholes_scenario(
            option,
            market,
            MarketShock(name="invalid_spot", spot_shift=-100.0),
        )


def test_scenario_rejects_negative_shocked_time_to_expiry() -> None:
    option = EuropeanOption(option_type="put", strike=100.0, time_to_expiry=0.5)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    with pytest.raises(DomainInputError, match="shocked time_to_expiry must be non-negative"):
        price_black_scholes_scenario(
            option,
            market,
            MarketShock(name="invalid_time", time_shift=-0.75),
        )

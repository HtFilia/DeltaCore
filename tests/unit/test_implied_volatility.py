import pytest

from derivatives_risk_engine.calibration.implied_vol import (
    solve_black_scholes_implied_volatility,
)
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.models.black_scholes import black_scholes_price


def test_black_scholes_implied_volatility_recovers_call_fixture_volatility() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )
    target_price = black_scholes_price(option, market)

    result = solve_black_scholes_implied_volatility(
        option=option,
        spot=market.spot,
        risk_free_rate=market.risk_free_rate,
        dividend_yield=market.dividend_yield,
        target_price=target_price,
    )

    assert result.model == "black_scholes"
    assert result.option_type == "call"
    assert result.implied_volatility == pytest.approx(0.20, abs=1e-12)
    assert result.diagnostics.converged is True
    assert result.diagnostics.objective_value <= 1e-12
    assert result.diagnostics.lower_bound == pytest.approx(1e-6)
    assert result.diagnostics.upper_bound == pytest.approx(5.0)
    assert result.diagnostics.failure_reason is None


def test_black_scholes_implied_volatility_recovers_put_with_dividends() -> None:
    option = EuropeanOption(option_type="put", strike=105.0, time_to_expiry=1.75)
    market = BlackScholesMarket(
        spot=98.0,
        risk_free_rate=0.0325,
        dividend_yield=0.011,
        volatility=0.24,
    )
    target_price = black_scholes_price(option, market)

    result = solve_black_scholes_implied_volatility(
        option=option,
        spot=market.spot,
        risk_free_rate=market.risk_free_rate,
        dividend_yield=market.dividend_yield,
        target_price=target_price,
    )

    assert result.option_type == "put"
    assert result.implied_volatility == pytest.approx(0.24, abs=1e-12)
    assert result.diagnostics.converged is True


def test_black_scholes_implied_volatility_reports_impossible_price() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)

    result = solve_black_scholes_implied_volatility(
        option=option,
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        target_price=101.0,
    )

    assert result.implied_volatility is None
    assert result.diagnostics.converged is False
    assert result.diagnostics.objective_value == pytest.approx(1.0, abs=1e-12)
    assert result.diagnostics.failure_reason == "target price is outside no-arbitrage bounds"


def test_black_scholes_implied_volatility_reports_expiry_failure() -> None:
    option = EuropeanOption(option_type="call", strike=95.0, time_to_expiry=0.0)

    result = solve_black_scholes_implied_volatility(
        option=option,
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        target_price=5.0,
    )

    assert result.implied_volatility is None
    assert result.diagnostics.converged is False
    assert result.diagnostics.failure_reason == "implied volatility is undefined at expiry"

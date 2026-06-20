from dataclasses import replace

import pytest

from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.models.black_scholes import black_scholes_price
from derivatives_risk_engine.numerics.finite_difference import (
    central_difference,
    second_order_central_difference,
)
from derivatives_risk_engine.risk.greeks import black_scholes_greeks


def test_black_scholes_call_greeks_match_closed_form_fixture() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    greeks = black_scholes_greeks(option, market)

    assert greeks.delta == pytest.approx(0.6368306511756191, abs=1e-12)
    assert greeks.gamma == pytest.approx(0.018762017345846895, abs=1e-12)
    assert greeks.vega == pytest.approx(37.52403469169379, abs=1e-12)
    assert greeks.theta == pytest.approx(-6.414027546438197, abs=1e-12)
    assert greeks.rho == pytest.approx(53.232481545376345, abs=1e-12)


def test_black_scholes_put_greeks_match_closed_form_fixture() -> None:
    option = EuropeanOption(option_type="put", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    greeks = black_scholes_greeks(option, market)

    assert greeks.delta == pytest.approx(-0.3631693488243809, abs=1e-12)
    assert greeks.gamma == pytest.approx(0.018762017345846895, abs=1e-12)
    assert greeks.vega == pytest.approx(37.52403469169379, abs=1e-12)
    assert greeks.theta == pytest.approx(-1.657880423934626, abs=1e-12)
    assert greeks.rho == pytest.approx(-41.89046090469506, abs=1e-12)


def test_black_scholes_greeks_match_finite_difference_estimates() -> None:
    option = EuropeanOption(option_type="call", strike=103.0, time_to_expiry=1.2)
    market = BlackScholesMarket(
        spot=98.0,
        risk_free_rate=0.025,
        dividend_yield=0.01,
        volatility=0.22,
    )

    greeks = black_scholes_greeks(option, market)

    delta_fd = central_difference(
        lambda spot: black_scholes_price(option, replace(market, spot=spot)),
        point=market.spot,
        bump=1e-3,
    )
    gamma_fd = second_order_central_difference(
        lambda spot: black_scholes_price(option, replace(market, spot=spot)),
        point=market.spot,
        bump=1e-2,
    )
    vega_fd = central_difference(
        lambda volatility: black_scholes_price(option, replace(market, volatility=volatility)),
        point=market.volatility,
        bump=1e-5,
    )
    rho_fd = central_difference(
        lambda risk_free_rate: black_scholes_price(
            option,
            replace(market, risk_free_rate=risk_free_rate),
        ),
        point=market.risk_free_rate,
        bump=1e-5,
    )
    theta_fd = -central_difference(
        lambda time_to_expiry: black_scholes_price(
            replace(option, time_to_expiry=time_to_expiry),
            market,
        ),
        point=option.time_to_expiry,
        bump=1e-5,
    )

    assert greeks.delta == pytest.approx(delta_fd, rel=1e-8)
    assert greeks.gamma == pytest.approx(gamma_fd, rel=1e-6)
    assert greeks.vega == pytest.approx(vega_fd, rel=1e-8)
    assert greeks.rho == pytest.approx(rho_fd, rel=1e-8)
    assert greeks.theta == pytest.approx(theta_fd, rel=1e-8)


def test_expired_black_scholes_greeks_are_rejected() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=0.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    with pytest.raises(ValueError, match="Greeks are undefined at expiry"):
        black_scholes_greeks(option, market)

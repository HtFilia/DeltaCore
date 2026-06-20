import math

import pytest

from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.models.black_scholes import black_scholes_price


def test_black_scholes_call_matches_closed_form_fixture() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    price = black_scholes_price(option, market)

    # Hull-style one-year ATM call fixture under continuous rates, tolerance near double precision.
    assert price == pytest.approx(10.450583572185565, abs=1e-12)


def test_black_scholes_put_matches_closed_form_fixture() -> None:
    option = EuropeanOption(option_type="put", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    price = black_scholes_price(option, market)

    # Same assumptions as the call fixture; this also anchors put sign conventions.
    assert price == pytest.approx(5.573526022256971, abs=1e-12)


def test_black_scholes_prices_satisfy_put_call_parity_with_dividends() -> None:
    call = EuropeanOption(option_type="call", strike=105.0, time_to_expiry=1.75)
    put = EuropeanOption(option_type="put", strike=105.0, time_to_expiry=1.75)
    market = BlackScholesMarket(
        spot=98.0,
        risk_free_rate=0.0325,
        dividend_yield=0.011,
        volatility=0.24,
    )

    call_price = black_scholes_price(call, market)
    put_price = black_scholes_price(put, market)

    discounted_forward_value = market.spot * math.exp(
        -market.dividend_yield * call.time_to_expiry
    ) - call.strike * math.exp(-market.risk_free_rate * call.time_to_expiry)
    assert call_price - put_price == pytest.approx(discounted_forward_value, abs=1e-12)


def test_expired_black_scholes_option_returns_intrinsic_value() -> None:
    call = EuropeanOption(option_type="call", strike=95.0, time_to_expiry=0.0)
    put = EuropeanOption(option_type="put", strike=105.0, time_to_expiry=0.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    assert black_scholes_price(call, market) == 5.0
    assert black_scholes_price(put, market) == 5.0

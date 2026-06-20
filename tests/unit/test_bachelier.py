import math

import pytest

from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BachelierMarket
from derivatives_risk_engine.models.bachelier import bachelier_price


def test_bachelier_call_matches_closed_form_fixture() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BachelierMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        normal_volatility=15.0,
    )

    price = bachelier_price(option, market)

    # Forward Bachelier fixture with continuous rates and annualized normal volatility.
    assert price == pytest.approx(8.460134478825838, abs=1e-12)


def test_bachelier_put_matches_closed_form_fixture() -> None:
    option = EuropeanOption(option_type="put", strike=100.0, time_to_expiry=1.0)
    market = BachelierMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        normal_volatility=15.0,
    )

    price = bachelier_price(option, market)

    assert price == pytest.approx(3.583076928897227, abs=1e-12)


def test_bachelier_prices_satisfy_put_call_parity_with_dividends() -> None:
    call = EuropeanOption(option_type="call", strike=105.0, time_to_expiry=1.75)
    put = EuropeanOption(option_type="put", strike=105.0, time_to_expiry=1.75)
    market = BachelierMarket(
        spot=98.0,
        risk_free_rate=0.0325,
        dividend_yield=0.011,
        normal_volatility=12.5,
    )

    call_price = bachelier_price(call, market)
    put_price = bachelier_price(put, market)

    discounted_forward_value = market.spot * math.exp(
        -market.dividend_yield * call.time_to_expiry
    ) - call.strike * math.exp(-market.risk_free_rate * call.time_to_expiry)
    assert call_price - put_price == pytest.approx(discounted_forward_value, abs=1e-12)


def test_expired_bachelier_option_returns_intrinsic_value() -> None:
    call = EuropeanOption(option_type="call", strike=95.0, time_to_expiry=0.0)
    put = EuropeanOption(option_type="put", strike=105.0, time_to_expiry=0.0)
    market = BachelierMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        normal_volatility=15.0,
    )

    assert bachelier_price(call, market) == 5.0
    assert bachelier_price(put, market) == 5.0

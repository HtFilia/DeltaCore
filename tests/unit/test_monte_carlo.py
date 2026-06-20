import pytest

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.models.black_scholes import black_scholes_price
from derivatives_risk_engine.numerics.monte_carlo import monte_carlo_black_scholes_price


def test_monte_carlo_black_scholes_price_is_deterministic_for_seed() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    first_result = monte_carlo_black_scholes_price(
        option=option,
        market=market,
        num_paths=50_000,
        seed=7,
    )
    second_result = monte_carlo_black_scholes_price(
        option=option,
        market=market,
        num_paths=50_000,
        seed=7,
    )

    assert first_result == second_result
    assert first_result.seed == 7
    assert first_result.num_paths == 50_000
    assert first_result.confidence_level == 0.95


def test_monte_carlo_confidence_interval_contains_closed_form_black_scholes_price() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    result = monte_carlo_black_scholes_price(
        option=option,
        market=market,
        num_paths=50_000,
        seed=7,
    )
    closed_form_price = black_scholes_price(option, market)

    assert result.price == pytest.approx(10.341148634251647, abs=1e-12)
    assert result.standard_error == pytest.approx(0.06508764791400842, abs=1e-12)
    assert result.confidence_interval_low <= closed_form_price <= result.confidence_interval_high
    assert result.confidence_interval_low == pytest.approx(10.213579188501766, abs=1e-12)
    assert result.confidence_interval_high == pytest.approx(10.468718080001528, abs=1e-12)


def test_expired_monte_carlo_option_returns_intrinsic_value_with_zero_error() -> None:
    option = EuropeanOption(option_type="put", strike=105.0, time_to_expiry=0.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    result = monte_carlo_black_scholes_price(
        option=option,
        market=market,
        num_paths=2,
        seed=7,
    )

    assert result.price == 5.0
    assert result.standard_error == 0.0
    assert result.confidence_interval_low == 5.0
    assert result.confidence_interval_high == 5.0


def test_monte_carlo_rejects_invalid_path_count() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    with pytest.raises(DomainInputError, match="num_paths must be at least 2"):
        monte_carlo_black_scholes_price(
            option=option,
            market=market,
            num_paths=1,
            seed=7,
        )


def test_monte_carlo_rejects_invalid_confidence_level() -> None:
    option = EuropeanOption(option_type="call", strike=100.0, time_to_expiry=1.0)
    market = BlackScholesMarket(
        spot=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    with pytest.raises(DomainInputError, match="confidence_level must be between 0 and 1"):
        monte_carlo_black_scholes_price(
            option=option,
            market=market,
            num_paths=1_000,
            seed=7,
            confidence_level=1.0,
        )

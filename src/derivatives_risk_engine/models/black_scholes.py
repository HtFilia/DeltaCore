from __future__ import annotations

import math

from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket

_SQRT_TWO = math.sqrt(2.0)


def _standard_normal_cdf(value: float) -> float:
    return 0.5 * math.erfc(-value / _SQRT_TWO)


def black_scholes_price(option: EuropeanOption, market: BlackScholesMarket) -> float:
    """Price a European option under Black-Scholes assumptions.

    The model assumes lognormal spot dynamics, continuous risk-free and dividend
    rates, annualized volatility, and ``time_to_expiry`` measured as a year fraction.
    At expiry the function returns intrinsic value.
    """
    if option.time_to_expiry == 0.0:
        if option.option_type == "call":
            return max(market.spot - option.strike, 0.0)
        return max(option.strike - market.spot, 0.0)

    sqrt_time = math.sqrt(option.time_to_expiry)
    volatility_time = market.volatility * sqrt_time
    log_moneyness = math.log(market.spot / option.strike)
    drift = market.risk_free_rate - market.dividend_yield
    d1 = (log_moneyness + (drift + 0.5 * market.volatility**2) * option.time_to_expiry) / (
        volatility_time
    )
    d2 = d1 - volatility_time

    discounted_spot = market.spot * math.exp(-market.dividend_yield * option.time_to_expiry)
    discounted_strike = option.strike * math.exp(-market.risk_free_rate * option.time_to_expiry)

    if option.option_type == "call":
        return discounted_spot * _standard_normal_cdf(d1) - discounted_strike * (
            _standard_normal_cdf(d2)
        )
    return discounted_strike * _standard_normal_cdf(-d2) - discounted_spot * (
        _standard_normal_cdf(-d1)
    )

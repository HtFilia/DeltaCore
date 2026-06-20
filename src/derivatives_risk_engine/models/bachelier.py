from __future__ import annotations

import math

from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BachelierMarket
from derivatives_risk_engine.numerics.normal import standard_normal_cdf, standard_normal_pdf


def bachelier_price(option: EuropeanOption, market: BachelierMarket) -> float:
    """Price a European option under the Bachelier normal model.

    The model uses the forward normal convention: the forward is
    ``spot * exp((risk_free_rate - dividend_yield) * time_to_expiry)``, the payoff
    is discounted at the continuously compounded risk-free rate, and
    ``normal_volatility`` is annualized in price units. At expiry the function
    returns intrinsic value.
    """
    if option.time_to_expiry == 0.0:
        if option.option_type == "call":
            return max(market.spot - option.strike, 0.0)
        return max(option.strike - market.spot, 0.0)

    sqrt_time = math.sqrt(option.time_to_expiry)
    normal_std_dev = market.normal_volatility * sqrt_time
    forward = market.spot * math.exp(
        (market.risk_free_rate - market.dividend_yield) * option.time_to_expiry
    )
    discount_factor = math.exp(-market.risk_free_rate * option.time_to_expiry)
    moneyness = forward - option.strike
    d = moneyness / normal_std_dev

    if option.option_type == "call":
        undiscounted_price = moneyness * standard_normal_cdf(d) + normal_std_dev * (
            standard_normal_pdf(d)
        )
    else:
        undiscounted_price = -moneyness * standard_normal_cdf(-d) + normal_std_dev * (
            standard_normal_pdf(d)
        )

    return discount_factor * undiscounted_price

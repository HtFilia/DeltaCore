from __future__ import annotations

import math
from dataclasses import dataclass

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.numerics.normal import standard_normal_cdf, standard_normal_pdf


@dataclass(frozen=True, slots=True)
class BlackScholesGreeks:
    """Black-Scholes Greeks for one European option.

    Conventions:
        delta: Price change per one spot unit.
        gamma: Delta change per one spot unit.
        vega: Price change per absolute volatility unit, so 1.0 equals 100 vol points.
        theta: Calendar-time decay per year, equivalent to ``-dV/dT``.
        rho: Price change per absolute continuously compounded rate unit.
    """

    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float


def black_scholes_greeks(
    option: EuropeanOption,
    market: BlackScholesMarket,
) -> BlackScholesGreeks:
    """Compute analytic Black-Scholes Greeks for a non-expired European option.

    Inputs use the same conventions as ``black_scholes_price``: continuous rates,
    continuous dividend yield, annualized lognormal volatility, and year-fraction
    time to expiry. Greeks at expiry are discontinuous or distribution-valued, so
    this function raises ``DomainInputError`` when ``time_to_expiry`` is zero.
    """
    if option.time_to_expiry == 0.0:
        raise DomainInputError("Greeks are undefined at expiry")

    sqrt_time = math.sqrt(option.time_to_expiry)
    volatility_time = market.volatility * sqrt_time
    log_moneyness = math.log(market.spot / option.strike)
    drift = market.risk_free_rate - market.dividend_yield
    d1 = (log_moneyness + (drift + 0.5 * market.volatility**2) * option.time_to_expiry) / (
        volatility_time
    )
    d2 = d1 - volatility_time

    dividend_discount = math.exp(-market.dividend_yield * option.time_to_expiry)
    rate_discount = math.exp(-market.risk_free_rate * option.time_to_expiry)
    pdf_d1 = standard_normal_pdf(d1)
    diffusion_decay = (
        market.spot * dividend_discount * pdf_d1 * market.volatility / (2.0 * sqrt_time)
    )

    gamma = dividend_discount * pdf_d1 / (market.spot * volatility_time)
    vega = market.spot * dividend_discount * pdf_d1 * sqrt_time

    if option.option_type == "call":
        delta = dividend_discount * standard_normal_cdf(d1)
        theta = (
            -diffusion_decay
            - market.risk_free_rate * option.strike * rate_discount * standard_normal_cdf(d2)
            + market.dividend_yield * market.spot * dividend_discount * standard_normal_cdf(d1)
        )
        rho = option.strike * option.time_to_expiry * rate_discount * standard_normal_cdf(d2)
    else:
        delta = dividend_discount * (standard_normal_cdf(d1) - 1.0)
        theta = (
            -diffusion_decay
            + market.risk_free_rate * option.strike * rate_discount * standard_normal_cdf(-d2)
            - market.dividend_yield * market.spot * dividend_discount * standard_normal_cdf(-d1)
        )
        rho = -option.strike * option.time_to_expiry * rate_discount * standard_normal_cdf(-d2)

    return BlackScholesGreeks(
        delta=delta,
        gamma=gamma,
        vega=vega,
        theta=theta,
        rho=rho,
    )

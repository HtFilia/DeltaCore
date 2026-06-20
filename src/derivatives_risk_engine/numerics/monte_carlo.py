from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.core.validation import require_finite


@dataclass(frozen=True, slots=True)
class MonteCarloPricingResult:
    """Monte Carlo pricing result with sampling uncertainty.

    Args:
        price: Discounted sample mean of simulated payoffs.
        standard_error: Standard error of the discounted sample mean.
        confidence_interval_low: Lower normal-approximation confidence bound.
        confidence_interval_high: Upper normal-approximation confidence bound.
        confidence_level: Confidence level used for the interval.
        num_paths: Number of Monte Carlo paths.
        seed: Explicit random seed used for deterministic reproducibility.
    """

    price: float
    standard_error: float
    confidence_interval_low: float
    confidence_interval_high: float
    confidence_level: float
    num_paths: int
    seed: int


def _validate_simulation_inputs(num_paths: int, seed: int, confidence_level: float) -> None:
    if num_paths < 2:
        raise DomainInputError("num_paths must be at least 2")
    if not isinstance(seed, int):
        raise DomainInputError("seed must be an integer")
    require_finite("confidence_level", confidence_level)
    if confidence_level <= 0.0 or confidence_level >= 1.0:
        raise DomainInputError("confidence_level must be between 0 and 1")


def _intrinsic_value(option: EuropeanOption, spot: float) -> float:
    if option.option_type == "call":
        return max(spot - option.strike, 0.0)
    return max(option.strike - spot, 0.0)


def monte_carlo_black_scholes_price(
    option: EuropeanOption,
    market: BlackScholesMarket,
    num_paths: int,
    seed: int,
    *,
    confidence_level: float = 0.95,
) -> MonteCarloPricingResult:
    """Price a European option by Monte Carlo under Black-Scholes dynamics.

    The simulation uses the risk-neutral terminal distribution
    ``S_T = S_0 exp((r - q - 0.5 sigma^2)T + sigma sqrt(T) Z)`` with
    ``Z`` sampled from a standard normal generator initialized by ``seed``.
    The returned confidence interval is a normal approximation around the
    discounted payoff mean.
    """
    _validate_simulation_inputs(num_paths=num_paths, seed=seed, confidence_level=confidence_level)

    if option.time_to_expiry == 0.0:
        price = _intrinsic_value(option, market.spot)
        return MonteCarloPricingResult(
            price=price,
            standard_error=0.0,
            confidence_interval_low=price,
            confidence_interval_high=price,
            confidence_level=confidence_level,
            num_paths=num_paths,
            seed=seed,
        )

    rng = np.random.default_rng(seed)
    standard_normals = rng.standard_normal(num_paths)
    sqrt_time = math.sqrt(option.time_to_expiry)
    drift = (
        market.risk_free_rate - market.dividend_yield - 0.5 * market.volatility * market.volatility
    )
    terminal_spots = market.spot * np.exp(
        drift * option.time_to_expiry + market.volatility * sqrt_time * standard_normals
    )

    if option.option_type == "call":
        payoffs = np.maximum(terminal_spots - option.strike, 0.0)
    else:
        payoffs = np.maximum(option.strike - terminal_spots, 0.0)

    discounted_payoffs = math.exp(-market.risk_free_rate * option.time_to_expiry) * payoffs
    price = float(np.mean(discounted_payoffs))
    standard_error = float(np.std(discounted_payoffs, ddof=1) / math.sqrt(num_paths))
    critical_value = NormalDist().inv_cdf(0.5 + confidence_level / 2.0)
    confidence_radius = critical_value * standard_error

    return MonteCarloPricingResult(
        price=price,
        standard_error=standard_error,
        confidence_interval_low=price - confidence_radius,
        confidence_interval_high=price + confidence_radius,
        confidence_level=confidence_level,
        num_paths=num_paths,
        seed=seed,
    )

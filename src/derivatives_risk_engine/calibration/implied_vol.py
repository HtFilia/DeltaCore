from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from derivatives_risk_engine.calibration.diagnostics import CalibrationDiagnostics
from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption, OptionType
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.core.validation import (
    require_finite,
    require_non_negative,
    require_positive,
)
from derivatives_risk_engine.models.black_scholes import black_scholes_price
from derivatives_risk_engine.numerics.root_finding import RootFindResult, brent_root


@dataclass(frozen=True, slots=True)
class BlackScholesImpliedVolatilityResult:
    """Black-Scholes implied-volatility calibration result."""

    model: Literal["black_scholes"]
    option_type: OptionType
    implied_volatility: float | None
    diagnostics: CalibrationDiagnostics


def _validate_inputs(
    spot: float,
    risk_free_rate: float,
    dividend_yield: float,
    target_price: float,
    lower_bound: float,
    upper_bound: float,
) -> None:
    require_positive("spot", spot)
    require_finite("risk_free_rate", risk_free_rate)
    require_finite("dividend_yield", dividend_yield)
    require_non_negative("target_price", target_price)
    require_positive("lower_bound", lower_bound)
    require_positive("upper_bound", upper_bound)
    if lower_bound >= upper_bound:
        raise DomainInputError("lower_bound must be less than upper_bound")


def _price_bounds(
    option: EuropeanOption,
    spot: float,
    risk_free_rate: float,
    dividend_yield: float,
) -> tuple[float, float]:
    discounted_spot = spot * math.exp(-dividend_yield * option.time_to_expiry)
    discounted_strike = option.strike * math.exp(-risk_free_rate * option.time_to_expiry)

    if option.option_type == "call":
        return max(discounted_spot - discounted_strike, 0.0), discounted_spot
    return max(discounted_strike - discounted_spot, 0.0), discounted_strike


def _failure_result(
    option: EuropeanOption,
    objective_value: float,
    lower_bound: float,
    upper_bound: float,
    failure_reason: str,
) -> BlackScholesImpliedVolatilityResult:
    return BlackScholesImpliedVolatilityResult(
        model="black_scholes",
        option_type=option.option_type,
        implied_volatility=None,
        diagnostics=CalibrationDiagnostics(
            converged=False,
            objective_value=objective_value,
            iterations=0,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            failure_reason=failure_reason,
        ),
    )


def _diagnostics_from_root_result(root_result: RootFindResult) -> CalibrationDiagnostics:
    return CalibrationDiagnostics(
        converged=root_result.converged,
        objective_value=root_result.objective_value,
        iterations=root_result.iterations,
        lower_bound=root_result.lower_bound,
        upper_bound=root_result.upper_bound,
        failure_reason=root_result.failure_reason,
    )


def solve_black_scholes_implied_volatility(
    option: EuropeanOption,
    spot: float,
    risk_free_rate: float,
    dividend_yield: float,
    target_price: float,
    *,
    lower_bound: float = 1e-6,
    upper_bound: float = 5.0,
    absolute_tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> BlackScholesImpliedVolatilityResult:
    """Solve Black-Scholes implied volatility from a target European option price.

    Args:
        option: European call or put with time to expiry as a year fraction.
        spot: Current underlying spot in the same currency units as strike.
        risk_free_rate: Continuously compounded annualized risk-free rate.
        dividend_yield: Continuously compounded annualized dividend yield.
        target_price: Observed option price to invert.
        lower_bound: Lower absolute volatility bound.
        upper_bound: Upper absolute volatility bound.
        absolute_tolerance: Absolute volatility tolerance for the root solver.
        max_iterations: Maximum root-finding iterations.

    Returns:
        Structured calibration result. Impossible prices and expiry cases return
        ``implied_volatility=None`` with a failure reason in diagnostics.
    """
    _validate_inputs(
        spot=spot,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
        target_price=target_price,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
    )

    if option.time_to_expiry == 0.0:
        intrinsic_value = (
            max(spot - option.strike, 0.0)
            if option.option_type == "call"
            else max(option.strike - spot, 0.0)
        )
        return _failure_result(
            option=option,
            objective_value=abs(target_price - intrinsic_value),
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            failure_reason="implied volatility is undefined at expiry",
        )

    minimum_price, maximum_price = _price_bounds(option, spot, risk_free_rate, dividend_yield)
    if target_price < minimum_price:
        return _failure_result(
            option=option,
            objective_value=minimum_price - target_price,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            failure_reason="target price is outside no-arbitrage bounds",
        )
    if target_price > maximum_price:
        return _failure_result(
            option=option,
            objective_value=target_price - maximum_price,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            failure_reason="target price is outside no-arbitrage bounds",
        )

    def objective(volatility: float) -> float:
        market = BlackScholesMarket(
            spot=spot,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=volatility,
        )
        return black_scholes_price(option, market) - target_price

    root_result = brent_root(
        objective,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        absolute_tolerance=absolute_tolerance,
        max_iterations=max_iterations,
    )

    return BlackScholesImpliedVolatilityResult(
        model="black_scholes",
        option_type=option.option_type,
        implied_volatility=root_result.root,
        diagnostics=_diagnostics_from_root_result(root_result),
    )

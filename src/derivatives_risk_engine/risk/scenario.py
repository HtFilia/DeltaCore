from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.core.validation import require_finite
from derivatives_risk_engine.models.black_scholes import black_scholes_price


@dataclass(frozen=True, slots=True)
class MarketShock:
    """Absolute market shock for deterministic scenario repricing.

    Args:
        name: Scenario name reported in results.
        spot_shift: Absolute spot shift in spot currency units.
        volatility_shift: Absolute lognormal-volatility shift, where 0.01 is 1 vol point.
        risk_free_rate_shift: Absolute continuously compounded rate shift.
        dividend_yield_shift: Absolute continuously compounded dividend-yield shift.
        time_shift: Absolute year-fraction shift to time to expiry.
    """

    name: str = "scenario"
    spot_shift: float = 0.0
    volatility_shift: float = 0.0
    risk_free_rate_shift: float = 0.0
    dividend_yield_shift: float = 0.0
    time_shift: float = 0.0

    def __post_init__(self) -> None:
        require_finite("spot_shift", self.spot_shift)
        require_finite("volatility_shift", self.volatility_shift)
        require_finite("risk_free_rate_shift", self.risk_free_rate_shift)
        require_finite("dividend_yield_shift", self.dividend_yield_shift)
        require_finite("time_shift", self.time_shift)


@dataclass(frozen=True, slots=True)
class ScenarioPnLResult:
    """Deterministic scenario PnL from repricing under a market shock."""

    model: Literal["black_scholes"]
    scenario_name: str
    shock: MarketShock
    base_price: float
    shocked_price: float
    pnl: float
    shocked_spot: float
    shocked_volatility: float
    shocked_risk_free_rate: float
    shocked_dividend_yield: float
    shocked_time_to_expiry: float


def _validate_shocked_inputs(
    shocked_spot: float,
    shocked_volatility: float,
    shocked_time_to_expiry: float,
) -> None:
    if shocked_spot <= 0.0:
        raise DomainInputError("shocked spot must be greater than zero")
    if shocked_volatility <= 0.0:
        raise DomainInputError("shocked volatility must be greater than zero")
    if shocked_time_to_expiry < 0.0:
        raise DomainInputError("shocked time_to_expiry must be non-negative")


def price_black_scholes_scenario(
    option: EuropeanOption,
    market: BlackScholesMarket,
    shock: MarketShock,
) -> ScenarioPnLResult:
    """Reprice a European option under an absolute Black-Scholes market shock.

    The scenario applies absolute shifts to spot, volatility, continuous rates,
    dividend yield, and time to expiry, then reprices with ``black_scholes_price``.
    PnL is reported as ``shocked_price - base_price``.
    """
    shocked_spot = market.spot + shock.spot_shift
    shocked_volatility = market.volatility + shock.volatility_shift
    shocked_risk_free_rate = market.risk_free_rate + shock.risk_free_rate_shift
    shocked_dividend_yield = market.dividend_yield + shock.dividend_yield_shift
    shocked_time_to_expiry = option.time_to_expiry + shock.time_shift
    _validate_shocked_inputs(
        shocked_spot=shocked_spot,
        shocked_volatility=shocked_volatility,
        shocked_time_to_expiry=shocked_time_to_expiry,
    )

    shocked_option = EuropeanOption(
        option_type=option.option_type,
        strike=option.strike,
        time_to_expiry=shocked_time_to_expiry,
    )
    shocked_market = BlackScholesMarket(
        spot=shocked_spot,
        risk_free_rate=shocked_risk_free_rate,
        dividend_yield=shocked_dividend_yield,
        volatility=shocked_volatility,
    )

    base_price = black_scholes_price(option, market)
    shocked_price = black_scholes_price(shocked_option, shocked_market)

    return ScenarioPnLResult(
        model="black_scholes",
        scenario_name=shock.name,
        shock=shock,
        base_price=base_price,
        shocked_price=shocked_price,
        pnl=shocked_price - base_price,
        shocked_spot=shocked_spot,
        shocked_volatility=shocked_volatility,
        shocked_risk_free_rate=shocked_risk_free_rate,
        shocked_dividend_yield=shocked_dividend_yield,
        shocked_time_to_expiry=shocked_time_to_expiry,
    )


def run_black_scholes_scenarios(
    option: EuropeanOption,
    market: BlackScholesMarket,
    shocks: tuple[MarketShock, ...],
) -> tuple[ScenarioPnLResult, ...]:
    """Run a deterministic batch of Black-Scholes scenario repricings."""
    return tuple(price_black_scholes_scenario(option, market, shock) for shock in shocks)

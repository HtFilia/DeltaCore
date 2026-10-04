"""Local Taylor contributions for one synthetic European option, in currency units."""

from dataclasses import dataclass

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.core.validation import require_finite
from derivatives_risk_engine.risk.greeks import BlackScholesGreeks, black_scholes_greeks
from derivatives_risk_engine.risk.scenario import MarketShock, price_black_scholes_scenario


@dataclass(frozen=True)
class AttributionShock:
    """Absolute spot/vol shifts and elapsed calendar years (365-day demo convention)."""

    name: str = "No shock"
    spot_shift: float = 0
    volatility_shift: float = 0
    elapsed_years: float = 0

    def __post_init__(self) -> None:
        for name in ("spot_shift", "volatility_shift", "elapsed_years"):
            require_finite(name, getattr(self, name))
        if self.elapsed_years < 0:
            raise DomainInputError("Elapsed calendar time must be non-negative")


@dataclass(frozen=True)
class AttributionResult:
    name: str
    base_price: float
    shocked_price: float
    full_pnl: float
    spot_delta: float
    spot_gamma: float
    vol_vega: float
    calendar_theta: float
    delta_only: float
    approximation: float
    residual: float
    shocked_spot: float
    shocked_volatility: float
    shocked_time_to_expiry: float
    greeks: BlackScholesGreeks
    limitations: str


def attribute_scenario(
    option: EuropeanOption, market: BlackScholesMarket, shock: AttributionShock
) -> AttributionResult:
    """Full repricing minus a base-state Taylor expansion, for one option unit.

    Vega is per absolute volatility unit; theta is calendar decay per year.
    The expansion omits cross/higher-order terms and is not an exact P&L attribution.
    """
    if option.time_to_expiry <= 0:
        raise DomainInputError(
            "Attribution requires positive base expiry; pricing remains available"
        )
    greeks = black_scholes_greeks(option, market)
    scenario = price_black_scholes_scenario(
        option,
        market,
        MarketShock(
            name=shock.name,
            spot_shift=shock.spot_shift,
            volatility_shift=shock.volatility_shift,
            time_shift=-shock.elapsed_years,
        ),
    )
    delta = greeks.delta * shock.spot_shift
    gamma = 0.5 * greeks.gamma * shock.spot_shift**2
    vega = greeks.vega * shock.volatility_shift
    theta = greeks.theta * shock.elapsed_years
    approximation = delta + gamma + vega + theta
    return AttributionResult(
        name=shock.name,
        base_price=scenario.base_price,
        shocked_price=scenario.shocked_price,
        full_pnl=scenario.pnl,
        spot_delta=delta,
        spot_gamma=gamma,
        vol_vega=vega,
        calendar_theta=theta,
        delta_only=delta,
        approximation=approximation,
        residual=scenario.pnl - approximation,
        shocked_spot=scenario.shocked_spot,
        shocked_volatility=scenario.shocked_volatility,
        shocked_time_to_expiry=scenario.shocked_time_to_expiry,
        greeks=greeks,
        limitations="Local expansion at the base; cross and higher-order terms omitted. "
        "Accuracy can deteriorate for large shocks and near expiry.",
    )

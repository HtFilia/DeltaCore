from collections.abc import Iterable

from derivatives_risk_engine.calibration.implied_vol import (
    BlackScholesImpliedVolatilityResult,
    solve_black_scholes_implied_volatility,
)
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.risk.greeks import BlackScholesGreeks, black_scholes_greeks
from derivatives_risk_engine.risk.scenario import (
    MarketShock,
    ScenarioPnLResult,
    run_black_scholes_scenarios,
)
from derivatives_risk_engine.risk.var import HistoricalRiskResult, historical_var_expected_shortfall


def compute_european_greeks(
    option: EuropeanOption,
    market: BlackScholesMarket,
) -> BlackScholesGreeks:
    """Compute analytic Black-Scholes Greeks for a European option."""
    return black_scholes_greeks(option=option, market=market)


def solve_european_implied_volatility(
    option: EuropeanOption,
    spot: float,
    risk_free_rate: float,
    dividend_yield: float,
    target_price: float,
    *,
    lower_bound: float,
    upper_bound: float,
) -> BlackScholesImpliedVolatilityResult:
    """Solve Black-Scholes implied volatility for a European option price."""
    return solve_black_scholes_implied_volatility(
        option=option,
        spot=spot,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
        target_price=target_price,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
    )


def compute_black_scholes_scenario_pnl(
    option: EuropeanOption,
    market: BlackScholesMarket,
    shocks: tuple[MarketShock, ...],
) -> tuple[ScenarioPnLResult, ...]:
    """Run deterministic Black-Scholes scenario repricings."""
    return run_black_scholes_scenarios(option=option, market=market, shocks=shocks)


def compute_historical_var_expected_shortfall(
    pnls: Iterable[float],
    *,
    confidence_level: float,
) -> HistoricalRiskResult:
    """Estimate historical VaR and Expected Shortfall from PnL observations."""
    return historical_var_expected_shortfall(pnls=pnls, confidence_level=confidence_level)

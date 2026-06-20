from dataclasses import dataclass

from derivatives_risk_engine.core.validation import require_finite, require_positive


@dataclass(frozen=True, slots=True)
class BlackScholesMarket:
    """Black-Scholes market inputs.

    Args:
        spot: Current underlying spot; must be positive.
        risk_free_rate: Continuously compounded annualized risk-free rate.
        dividend_yield: Continuously compounded annualized dividend yield.
        volatility: Annualized lognormal volatility; must be positive.
    """

    spot: float
    risk_free_rate: float
    dividend_yield: float
    volatility: float

    def __post_init__(self) -> None:
        require_positive("spot", self.spot)
        require_finite("risk_free_rate", self.risk_free_rate)
        require_finite("dividend_yield", self.dividend_yield)
        require_positive("volatility", self.volatility)

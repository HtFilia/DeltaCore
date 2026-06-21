from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from derivatives_risk_engine.core.instruments import OptionType


class EuropeanPricingRequest(BaseModel):
    """Request for Black-Scholes European option pricing.

    Units use spot/strike in the same currency, year-fraction time to expiry,
    continuous annualized rates, and annualized lognormal volatility.
    """

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    option_type: OptionType
    spot: float = Field(gt=0.0)
    strike: float = Field(gt=0.0)
    time_to_expiry: float = Field(ge=0.0)
    risk_free_rate: float
    dividend_yield: float = 0.0
    volatility: float = Field(gt=0.0)


class EuropeanPricingResponse(BaseModel):
    """Response for a European option pricing request."""

    model: Literal["black_scholes"]
    option_type: OptionType
    price: float
    convention: Literal["continuous_rates_annualized_volatility"]


class EuropeanGreeksRequest(EuropeanPricingRequest):
    """Request for analytic Black-Scholes Greeks."""


class EuropeanGreeksResponse(BaseModel):
    """Response for analytic Black-Scholes Greeks."""

    model: Literal["black_scholes"]
    option_type: OptionType
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    convention: Literal["continuous_rates_annualized_volatility"]


class ImpliedVolatilityRequest(BaseModel):
    """Request for Black-Scholes implied-volatility calibration."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    option_type: OptionType
    spot: float = Field(gt=0.0)
    strike: float = Field(gt=0.0)
    time_to_expiry: float = Field(ge=0.0)
    risk_free_rate: float
    dividend_yield: float = 0.0
    target_price: float = Field(ge=0.0)
    lower_bound: float = Field(default=1e-6, gt=0.0)
    upper_bound: float = Field(default=5.0, gt=0.0)


class CalibrationDiagnosticsResponse(BaseModel):
    """Response diagnostics for a calibration routine."""

    converged: bool
    objective_value: float
    iterations: int
    lower_bound: float
    upper_bound: float
    failure_reason: str | None


class ImpliedVolatilityResponse(BaseModel):
    """Response for Black-Scholes implied-volatility calibration."""

    model: Literal["black_scholes"]
    option_type: OptionType
    implied_volatility: float | None
    diagnostics: CalibrationDiagnosticsResponse


class MarketShockRequest(BaseModel):
    """Absolute market shock for scenario PnL requests."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    name: str = "scenario"
    spot_shift: float = 0.0
    volatility_shift: float = 0.0
    risk_free_rate_shift: float = 0.0
    dividend_yield_shift: float = 0.0
    time_shift: float = 0.0


class ScenarioPnLRequest(EuropeanPricingRequest):
    """Request for deterministic Black-Scholes scenario PnL."""

    shocks: list[MarketShockRequest] = Field(min_length=1)


class ScenarioPnLItemResponse(BaseModel):
    """One deterministic scenario repricing result."""

    scenario_name: str
    base_price: float
    shocked_price: float
    pnl: float
    shocked_spot: float
    shocked_volatility: float
    shocked_risk_free_rate: float
    shocked_dividend_yield: float
    shocked_time_to_expiry: float


class ScenarioPnLResponse(BaseModel):
    """Response for deterministic scenario PnL."""

    model: Literal["black_scholes"]
    convention: Literal["absolute_market_shocks"]
    results: list[ScenarioPnLItemResponse]


class HistoricalVarRequest(BaseModel):
    """Request for historical VaR and Expected Shortfall."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    pnls: list[float] = Field(min_length=2)
    confidence_level: float = Field(default=0.95, gt=0.0, lt=1.0)


class HistoricalVarResponse(BaseModel):
    """Response for historical VaR and Expected Shortfall."""

    method: Literal["historical"]
    confidence_level: float
    value_at_risk: float
    expected_shortfall: float
    num_observations: int
    tail_observations: int
    quantile_index: int

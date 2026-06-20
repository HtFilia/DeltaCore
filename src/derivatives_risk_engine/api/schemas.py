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

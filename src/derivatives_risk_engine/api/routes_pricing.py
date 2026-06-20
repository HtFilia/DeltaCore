from fastapi import APIRouter, HTTPException

from derivatives_risk_engine.api.schemas import (
    EuropeanPricingRequest,
    EuropeanPricingResponse,
)
from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.services.pricing_service import price_european_option

router = APIRouter()


@router.post("/price/european", response_model=EuropeanPricingResponse)
def price_european(request: EuropeanPricingRequest) -> EuropeanPricingResponse:
    """Price a European call or put under Black-Scholes assumptions."""
    try:
        result = price_european_option(
            option=EuropeanOption(
                option_type=request.option_type,
                strike=request.strike,
                time_to_expiry=request.time_to_expiry,
            ),
            market=BlackScholesMarket(
                spot=request.spot,
                risk_free_rate=request.risk_free_rate,
                dividend_yield=request.dividend_yield,
                volatility=request.volatility,
            ),
        )
    except DomainInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return EuropeanPricingResponse(
        model="black_scholes",
        option_type=result.option_type,
        price=result.price,
        convention="continuous_rates_annualized_volatility",
    )

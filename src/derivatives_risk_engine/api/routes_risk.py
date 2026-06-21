from fastapi import APIRouter, HTTPException

from derivatives_risk_engine.api.schemas import (
    CalibrationDiagnosticsResponse,
    EuropeanGreeksRequest,
    EuropeanGreeksResponse,
    HistoricalVarRequest,
    HistoricalVarResponse,
    ImpliedVolatilityRequest,
    ImpliedVolatilityResponse,
    ScenarioPnLItemResponse,
    ScenarioPnLRequest,
    ScenarioPnLResponse,
)
from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.instruments import EuropeanOption, OptionType
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.risk.scenario import MarketShock
from derivatives_risk_engine.services.pricing_service import BLACK_SCHOLES_MODEL, PRICING_CONVENTION
from derivatives_risk_engine.services.risk_service import (
    compute_black_scholes_scenario_pnl,
    compute_european_greeks,
    compute_historical_var_expected_shortfall,
    solve_european_implied_volatility,
)

router = APIRouter()


def _option_from_request(
    option_type: OptionType,
    strike: float,
    time_to_expiry: float,
) -> EuropeanOption:
    return EuropeanOption(
        option_type=option_type,
        strike=strike,
        time_to_expiry=time_to_expiry,
    )


def _market_from_request(
    spot: float,
    risk_free_rate: float,
    dividend_yield: float,
    volatility: float,
) -> BlackScholesMarket:
    return BlackScholesMarket(
        spot=spot,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
        volatility=volatility,
    )


@router.post("/greeks/european", response_model=EuropeanGreeksResponse)
def greeks_european(request: EuropeanGreeksRequest) -> EuropeanGreeksResponse:
    """Compute analytic Black-Scholes Greeks for a European option."""
    try:
        greeks = compute_european_greeks(
            option=_option_from_request(
                option_type=request.option_type,
                strike=request.strike,
                time_to_expiry=request.time_to_expiry,
            ),
            market=_market_from_request(
                spot=request.spot,
                risk_free_rate=request.risk_free_rate,
                dividend_yield=request.dividend_yield,
                volatility=request.volatility,
            ),
        )
    except DomainInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return EuropeanGreeksResponse(
        model=BLACK_SCHOLES_MODEL,
        option_type=request.option_type,
        delta=greeks.delta,
        gamma=greeks.gamma,
        vega=greeks.vega,
        theta=greeks.theta,
        rho=greeks.rho,
        convention=PRICING_CONVENTION,
    )


@router.post("/implied-volatility", response_model=ImpliedVolatilityResponse)
def implied_volatility(request: ImpliedVolatilityRequest) -> ImpliedVolatilityResponse:
    """Solve Black-Scholes implied volatility for a European option price."""
    try:
        result = solve_european_implied_volatility(
            option=_option_from_request(
                option_type=request.option_type,
                strike=request.strike,
                time_to_expiry=request.time_to_expiry,
            ),
            spot=request.spot,
            risk_free_rate=request.risk_free_rate,
            dividend_yield=request.dividend_yield,
            target_price=request.target_price,
            lower_bound=request.lower_bound,
            upper_bound=request.upper_bound,
        )
    except DomainInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ImpliedVolatilityResponse(
        model=result.model,
        option_type=result.option_type,
        implied_volatility=result.implied_volatility,
        diagnostics=CalibrationDiagnosticsResponse(
            converged=result.diagnostics.converged,
            objective_value=result.diagnostics.objective_value,
            iterations=result.diagnostics.iterations,
            lower_bound=result.diagnostics.lower_bound,
            upper_bound=result.diagnostics.upper_bound,
            failure_reason=result.diagnostics.failure_reason,
        ),
    )


@router.post("/risk/scenario-pnl", response_model=ScenarioPnLResponse)
def scenario_pnl(request: ScenarioPnLRequest) -> ScenarioPnLResponse:
    """Run deterministic Black-Scholes scenario PnL repricings."""
    try:
        results = compute_black_scholes_scenario_pnl(
            option=_option_from_request(
                option_type=request.option_type,
                strike=request.strike,
                time_to_expiry=request.time_to_expiry,
            ),
            market=_market_from_request(
                spot=request.spot,
                risk_free_rate=request.risk_free_rate,
                dividend_yield=request.dividend_yield,
                volatility=request.volatility,
            ),
            shocks=tuple(
                MarketShock(
                    name=shock.name,
                    spot_shift=shock.spot_shift,
                    volatility_shift=shock.volatility_shift,
                    risk_free_rate_shift=shock.risk_free_rate_shift,
                    dividend_yield_shift=shock.dividend_yield_shift,
                    time_shift=shock.time_shift,
                )
                for shock in request.shocks
            ),
        )
    except DomainInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ScenarioPnLResponse(
        model=BLACK_SCHOLES_MODEL,
        convention="absolute_market_shocks",
        results=[
            ScenarioPnLItemResponse(
                scenario_name=result.scenario_name,
                base_price=result.base_price,
                shocked_price=result.shocked_price,
                pnl=result.pnl,
                shocked_spot=result.shocked_spot,
                shocked_volatility=result.shocked_volatility,
                shocked_risk_free_rate=result.shocked_risk_free_rate,
                shocked_dividend_yield=result.shocked_dividend_yield,
                shocked_time_to_expiry=result.shocked_time_to_expiry,
            )
            for result in results
        ],
    )


@router.post("/risk/historical-var", response_model=HistoricalVarResponse)
def historical_var(request: HistoricalVarRequest) -> HistoricalVarResponse:
    """Estimate historical VaR and Expected Shortfall from PnL observations."""
    try:
        result = compute_historical_var_expected_shortfall(
            pnls=request.pnls,
            confidence_level=request.confidence_level,
        )
    except DomainInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return HistoricalVarResponse(
        method=result.method,
        confidence_level=result.confidence_level,
        value_at_risk=result.value_at_risk,
        expected_shortfall=result.expected_shortfall,
        num_observations=result.num_observations,
        tail_observations=result.tail_observations,
        quantile_index=result.quantile_index,
    )

from dataclasses import dataclass

from derivatives_risk_engine.core.instruments import EuropeanOption, OptionType
from derivatives_risk_engine.core.market import BlackScholesMarket
from derivatives_risk_engine.models.black_scholes import black_scholes_price

BLACK_SCHOLES_MODEL = "black_scholes"
PRICING_CONVENTION = "continuous_rates_annualized_volatility"


@dataclass(frozen=True, slots=True)
class EuropeanPricingResult:
    """European option pricing result with the model and convention used."""

    model: str
    option_type: OptionType
    price: float
    convention: str


def price_european_option(
    option: EuropeanOption,
    market: BlackScholesMarket,
) -> EuropeanPricingResult:
    """Price a European option with the currently supported Black-Scholes model."""
    return EuropeanPricingResult(
        model=BLACK_SCHOLES_MODEL,
        option_type=option.option_type,
        price=black_scholes_price(option, market),
        convention=PRICING_CONVENTION,
    )

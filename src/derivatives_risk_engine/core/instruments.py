from dataclasses import dataclass
from typing import Literal

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.validation import require_non_negative, require_positive

OptionType = Literal["call", "put"]


@dataclass(frozen=True, slots=True)
class EuropeanOption:
    """European option contract.

    Args:
        option_type: ``"call"`` or ``"put"``.
        strike: Strike price in the same currency units as spot; must be positive.
        time_to_expiry: Year fraction to expiry; must be non-negative.
    """

    option_type: OptionType
    strike: float
    time_to_expiry: float

    def __post_init__(self) -> None:
        if self.option_type not in {"call", "put"}:
            raise DomainInputError("option_type must be 'call' or 'put'")
        require_positive("strike", self.strike)
        require_non_negative("time_to_expiry", self.time_to_expiry)

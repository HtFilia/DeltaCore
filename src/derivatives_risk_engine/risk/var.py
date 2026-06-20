from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.validation import require_finite


@dataclass(frozen=True, slots=True)
class HistoricalRiskResult:
    """Historical VaR and Expected Shortfall from deterministic PnL observations.

    Conventions:
        PnL observations are positive for gains and negative for losses.
        Losses are computed as ``-PnL``.
        ``value_at_risk`` is the conservative empirical loss quantile at the
        requested confidence level.
        ``expected_shortfall`` is the arithmetic mean of losses at or beyond
        that quantile, including the VaR observation.
    """

    method: Literal["historical"]
    confidence_level: float
    value_at_risk: float
    expected_shortfall: float
    num_observations: int
    tail_observations: int
    quantile_index: int


def _validate_confidence_level(confidence_level: float) -> None:
    require_finite("confidence_level", confidence_level)
    if confidence_level <= 0.0 or confidence_level >= 1.0:
        raise DomainInputError("confidence_level must be between 0 and 1")


def _validated_pnls(pnls: Iterable[float]) -> tuple[float, ...]:
    pnl_values = tuple(pnls)
    if len(pnl_values) < 2:
        raise DomainInputError("pnls must contain at least 2 observations")

    for index, pnl in enumerate(pnl_values):
        require_finite(f"pnls[{index}]", pnl)

    return pnl_values


def historical_var_expected_shortfall(
    pnls: Iterable[float],
    *,
    confidence_level: float = 0.95,
) -> HistoricalRiskResult:
    """Estimate historical VaR and Expected Shortfall from PnL observations.

    Args:
        pnls: Deterministic PnL observations where positive values are gains and
            negative values are losses. No live market data is read.
        confidence_level: Confidence level for the empirical loss quantile,
            strictly between 0 and 1.

    Returns:
        Historical risk metrics using losses sorted in ascending order. The
        empirical quantile index is ``ceil(confidence_level * n) - 1`` with
        zero-based indexing. Expected Shortfall averages the quantile loss and
        all more severe losses.
    """
    _validate_confidence_level(confidence_level)
    pnl_values = _validated_pnls(pnls)

    sorted_losses = tuple(sorted(-pnl for pnl in pnl_values))
    quantile_index = max(math.ceil(confidence_level * len(sorted_losses)) - 1, 0)
    tail_losses = sorted_losses[quantile_index:]
    value_at_risk = sorted_losses[quantile_index]
    expected_shortfall = sum(tail_losses) / len(tail_losses)

    return HistoricalRiskResult(
        method="historical",
        confidence_level=confidence_level,
        value_at_risk=value_at_risk,
        expected_shortfall=expected_shortfall,
        num_observations=len(sorted_losses),
        tail_observations=len(tail_losses),
        quantile_index=quantile_index,
    )

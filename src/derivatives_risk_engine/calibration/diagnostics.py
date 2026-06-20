from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CalibrationDiagnostics:
    """Diagnostics reported by a calibration routine.

    Args:
        converged: Whether the numerical calibration reached a valid solution.
        objective_value: Absolute residual or distance to the feasible region.
        iterations: Number of numerical iterations performed.
        lower_bound: Lower calibrated parameter bound.
        upper_bound: Upper calibrated parameter bound.
        failure_reason: Structured failure reason when ``converged`` is false.
    """

    converged: bool
    objective_value: float
    iterations: int
    lower_bound: float
    upper_bound: float
    failure_reason: str | None

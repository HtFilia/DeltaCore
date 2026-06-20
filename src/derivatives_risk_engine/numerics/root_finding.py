from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from scipy.optimize import brentq  # type: ignore[import-untyped]

from derivatives_risk_engine.core.exceptions import DomainInputError
from derivatives_risk_engine.core.validation import require_finite, require_positive


@dataclass(frozen=True, slots=True)
class RootFindResult:
    """Result from a bracketed one-dimensional root solve."""

    root: float | None
    converged: bool
    objective_value: float
    iterations: int
    lower_bound: float
    upper_bound: float
    failure_reason: str | None


def _validate_bounds(lower_bound: float, upper_bound: float) -> None:
    require_finite("lower_bound", lower_bound)
    require_finite("upper_bound", upper_bound)
    if lower_bound >= upper_bound:
        raise DomainInputError("lower_bound must be less than upper_bound")


def _evaluate(function: Callable[[float], float], point: float) -> float:
    value = function(point)
    require_finite("function evaluation", value)
    return value


def brent_root(
    function: Callable[[float], float],
    lower_bound: float,
    upper_bound: float,
    *,
    absolute_tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> RootFindResult:
    """Solve a scalar bracketed root problem with Brent's method.

    Args:
        function: Deterministic scalar function.
        lower_bound: Lower endpoint for the root bracket.
        upper_bound: Upper endpoint for the root bracket.
        absolute_tolerance: Absolute tolerance passed to SciPy's Brent solver.
        max_iterations: Maximum number of solver iterations.

    Returns:
        A structured result. Bracketing failures are returned with
        ``converged=False`` rather than being silently swallowed.
    """
    _validate_bounds(lower_bound, upper_bound)
    require_positive("absolute_tolerance", absolute_tolerance)
    require_positive("max_iterations", float(max_iterations))

    lower_value = _evaluate(function, lower_bound)
    upper_value = _evaluate(function, upper_bound)

    if lower_value == 0.0:
        return RootFindResult(
            root=lower_bound,
            converged=True,
            objective_value=0.0,
            iterations=0,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            failure_reason=None,
        )
    if upper_value == 0.0:
        return RootFindResult(
            root=upper_bound,
            converged=True,
            objective_value=0.0,
            iterations=0,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            failure_reason=None,
        )
    if lower_value * upper_value > 0.0:
        return RootFindResult(
            root=None,
            converged=False,
            objective_value=min(abs(lower_value), abs(upper_value)),
            iterations=0,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            failure_reason="root is not bracketed by the supplied bounds",
        )

    root, solver_result = brentq(
        function,
        lower_bound,
        upper_bound,
        xtol=absolute_tolerance,
        maxiter=max_iterations,
        full_output=True,
        disp=False,
    )
    objective_value = abs(_evaluate(function, float(root)))
    converged = bool(solver_result.converged)

    return RootFindResult(
        root=float(root) if converged else None,
        converged=converged,
        objective_value=objective_value,
        iterations=cast(int, solver_result.iterations),
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        failure_reason=None if converged else "root solver did not converge",
    )

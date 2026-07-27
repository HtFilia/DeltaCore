# Contributing

## Scope and architecture

DeltaCore is a Python backend for derivatives pricing, Greeks, volatility
calibration, and market-risk analytics. Keep dependency flow directed from the
API through services into pure domain, model, numerical, calibration, and risk
modules. Domain code must not depend on FastAPI.

Backend code must remain Python-only. Libraries with native internals are
welcome when they serve a documented numerical purpose, but custom native
extensions are out of scope.

## Engineering requirements

- Use typed Pydantic models at API boundaries.
- Keep pricing kernels pure and deterministic: no hidden network calls, mutable
  globals, or wall-clock dependencies.
- Use explicit seeds for stochastic tests and examples.
- Document public functions with inputs, units, conventions, and numerical
  assumptions.
- Surface numerical failures through structured errors or domain-specific
  exceptions.
- Keep tests independent of live market data by using small, documented,
  synthetic fixtures.
- Update public documentation when behavior or model coverage changes.

## Numerical validation

Every pricing model needs at least one independent validation, such as a
closed-form reference, limiting case, put-call parity check, finite-difference
comparison, or regression fixture.

Greeks must state bump convention, units, annualization, and sign. Calibration
results must expose convergence status, objective value, parameter bounds, and
failure reason. Monte Carlo outputs exposed to users must include standard error
or a confidence interval. Do not describe unvalidated or toy models as
production-accurate.

## Local quality gate

```bash
uv sync --extra dev
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

Changes are ready when typing, tests, numerical invariants, and affected
documentation all agree.

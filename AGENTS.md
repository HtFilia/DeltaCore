# AGENTS.md

## Repository mission

Build a production-quality Python backend for derivatives pricing, Greeks, volatility calibration, and market-risk analytics. The repository must demonstrate quantitative-finance depth, numerical rigor, clean API design, tests, and documentation.

## Read first

Before changing code, read these files in order:

1. `README.md`
2. `docs/PROJECT_SPEC.md`
3. `docs/ARCHITECTURE.md`
4. `docs/QUALITY_AND_VALIDATION.md`
5. `PLANS.md`

## Python-only constraint

- Backend code must be written in Python.
- Do not add C++, Rust, Java, Go, or custom native extensions.
- Python libraries with native internals are allowed: NumPy, SciPy, pandas, FastAPI, Pydantic, JAX if added deliberately.
- Keep formulas and numerical assumptions explicit in docs and tests.

## Expected layout

```text
src/derivatives_risk_engine/
  api/              # FastAPI app, request/response schemas
  core/             # pure pricing/risk domain logic
  models/           # option, curve, volatility, market-data models
  numerics/         # Monte Carlo, root finding, interpolation, finite differences
  calibration/      # implied vol and model calibration routines
  risk/             # Greeks, VaR, ES, stress testing
  services/         # orchestration between API and domain logic
  utils/            # small utilities only

tests/
  unit/
  integration/
  numerical_regression/

docs/
benchmarks/
notebooks/
```

## Development commands

Prefer `uv`. If the project is not bootstrapped yet, create `pyproject.toml` first.

```bash
uv sync --extra dev
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv run pytest tests/numerical_regression
```

FastAPI smoke test once an API exists:

```bash
uv run uvicorn derivatives_risk_engine.api.main:app --reload
```

## Engineering rules

- Use typed Pydantic models for API boundaries.
- Keep pricing kernels pure and deterministic; no hidden network calls, mutable globals, or wall-clock dependencies.
- Use explicit random seeds for stochastic tests and examples.
- Prefer vectorized NumPy/SciPy implementations where clarity is preserved.
- Add docstrings to public functions explaining inputs, units, conventions, and numerical assumptions.
- Do not silently catch numerical failures. Return structured errors or raise domain-specific exceptions.
- Avoid live market data in tests. Use small fixtures and documented synthetic surfaces.

## Quantitative rules

- Every pricing model needs at least one independent validation: closed-form reference, limiting case, put-call parity, finite-difference check, or regression fixture.
- Greeks must specify convention: bump size, absolute/relative bump, units, annualization, and sign.
- Calibration routines must report objective value, convergence status, parameter bounds, and failure reason.
- Monte Carlo results must include confidence intervals or standard error when exposed to users.
- Do not present toy pricing as production-accurate for exotic products.

## Definition of done

A task is done only when:

- Implementation is typed and covered by tests.
- Numerical behavior is validated against an explicit invariant or reference value.
- `ruff`, `mypy`, and `pytest` pass for the relevant scope.
- README or docs are updated if public behavior changed.
- Codex final response lists changed files, checks run, and known limitations.

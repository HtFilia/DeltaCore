# Quality and validation

## Test categories

### Unit tests

Fast tests for formulas, schemas, and pure functions.

Examples:

- Black-Scholes call/put values against known fixtures.
- Bachelier call/put values against known forward-normal fixtures.
- Put-call parity.
- Monotonicity of option price with respect to volatility.
- Input validation failures.

### Numerical regression tests

Tests that protect against accidental changes in numerical behavior.

Examples:

- Fixed option grids with expected prices.
- Analytic Black-Scholes Greeks versus finite-difference Greeks with documented absolute bumps.
- Monte Carlo price within confidence interval for a fixed seed.

### Integration tests

Tests that call API routes via FastAPI test client.

Examples:

- `/price/european` returns expected schema.
- Invalid request returns structured validation error.

## Numerical validation checklist

For each model or method, document:

- Formula or algorithm.
- Units and conventions.
- Reference implementation or invariant.
- Expected tolerance.
- Known failure modes.

## Recommended checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Benchmarking principles

- Benchmarks are not correctness tests.
- Keep benchmark data synthetic and deterministic.
- Report environment and input size.
- Compare naive vs vectorized implementation only when the comparison teaches something.

## Documentation quality bar

Every major feature should include:

- One paragraph explaining the financial purpose.
- One paragraph explaining the numerical method.
- One example request/response or Python call.
- One limitation note.

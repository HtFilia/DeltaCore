# DeltaCore architecture

## Design principles

- Domain code should not depend on FastAPI.
- API schemas should translate external requests into internal domain objects.
- Numerical methods should be independently testable.
- Stochastic components must be deterministic under explicit seeds.

## Proposed module boundaries

```text
api/
  main.py                # FastAPI app factory
  routes_pricing.py      # pricing routes
  routes_risk.py         # risk routes
  schemas.py             # Pydantic request/response contracts

core/
  instruments.py         # option/instrument entities
  market.py              # spot, rates, dividends, vol assumptions
  conventions.py         # day-count, compounding, units

models/
  black_scholes.py       # closed-form lognormal model
  bachelier.py           # normal model

numerics/
  finite_difference.py
  root_finding.py
  monte_carlo.py
  random.py

calibration/
  implied_vol.py
  diagnostics.py

risk/
  greeks.py
  scenario.py
  var.py

services/
  pricing_service.py
  risk_service.py
```

## Dependency direction

```text
api -> services -> core/models/numerics/risk
```

Never import `api` from `core`, `models`, `numerics`, `calibration`, or `risk`.

## Public API design

Use service functions for backend logic:

```python
price_european_option(request: EuropeanPricingRequest) -> EuropeanPricingResult
compute_european_greeks(request: EuropeanGreekRequest) -> EuropeanGreekResult
solve_implied_volatility(request: ImpliedVolRequest) -> ImpliedVolResult
```

## Numerical reproducibility

- Use deterministic fixtures for regression tests.
- Store tolerance choices in tests with a comment explaining why the tolerance is appropriate.
- Separate fast unit tests from slower Monte Carlo regression tests.

## Future extensions

- SABR/Heston calibration.
- JAX-based autodiff Greeks.
- Async job endpoint for larger risk runs.
- OpenAPI examples and generated client.

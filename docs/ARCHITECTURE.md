# DeltaCore architecture

## Design principles

- Domain code should not depend on FastAPI.
- API schemas should translate external requests into internal domain objects.
- Numerical methods should be independently testable.
- Stochastic components must be deterministic under explicit seeds.

## Module boundaries

```text
api/
  main.py                # FastAPI app factory
  routes_demo.py         # browser demo route
  routes_pricing.py      # pricing routes
  routes_risk.py         # risk routes
  schemas.py             # Pydantic request/response contracts
  static/                # demo page (HTML, CSS, JS)

core/
  instruments.py         # option/instrument entities
  market.py              # spot, rates, dividends, vol assumptions
  validation.py          # input checks shared by the models
  exceptions.py          # input error types

models/
  black_scholes.py       # closed-form lognormal model
  bachelier.py           # normal model

numerics/
  finite_difference.py
  root_finding.py
  monte_carlo.py
  normal.py

calibration/
  implied_vol.py
  diagnostics.py

risk/
  attribution.py         # Greek attribution of scenario P&L
  greeks.py
  scenario.py
  var.py

services/
  pricing_service.py
  risk_service.py
```

## Dependency direction

```text
api -> services -> core/models/numerics/calibration/risk
```

Never import `api` from `core`, `models`, `numerics`, `calibration`, or `risk`.

## Public API design

Use service functions for backend logic:

```python
price_european_option(request: EuropeanPricingRequest) -> EuropeanPricingResult
compute_european_greeks(request: EuropeanGreekRequest) -> EuropeanGreekResult
solve_implied_volatility(request: ImpliedVolRequest) -> ImpliedVolResult
compute_black_scholes_scenario_pnl(...) -> tuple[ScenarioPnLResult, ...]
compute_historical_var_expected_shortfall(...) -> HistoricalRiskResult
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

# DeltaCore project specification

## Objective

Create DeltaCore: a Python backend that prices vanilla European options, computes Greeks, inverts prices for implied volatility, and exposes risk analytics through a typed API. Each item below states whether it is implemented or planned.

## Target users

- Quant researchers who want a readable pricing sandbox.
- Quant developers who want a clean Python backend example.
- Risk analysts who need reproducible stress-testing examples.

## In scope

### Pricing

- European call/put under Black-Scholes (implemented; served by the API).
- European call/put under Bachelier/normal model (implemented in the library; not served by the API).
- Digital options (planned, optional).
- Monte Carlo pricing for vanilla options (implemented in the library with standard error and confidence interval; API exposure planned).

### Greeks

- Delta, gamma, vega, theta, rho under Black-Scholes (implemented, closed form).
- Finite-difference derivatives (implemented as numerical helpers, used by tests rather than as a runtime fallback).
- Comparison tests between analytic and numerical Greeks (implemented).

### Calibration

- Black-Scholes implied volatility via bounded root finding (implemented).
- Smile calibration to simple parametric forms (planned).
- Solver diagnostics and structured failure reasons (implemented).

### Risk

- Scenario PnL with spot, volatility, rate, dividend and time shocks (implemented).
- Greek attribution of a scenario with its residual (implemented).
- Historical VaR and Expected Shortfall (implemented); simulated VaR (planned).

### API

Implemented:

- `GET /health`
- `POST /price/european`
- `POST /greeks/european`
- `POST /implied-volatility`
- `POST /risk/scenario-pnl`
- `POST /risk/scenario-attribution`
- `POST /risk/historical-var`
- `GET /demo` and `GET /demo-meta` for the browser demonstration backed by API calls

## Out of scope for the first version

- Real-time market-data ingestion.
- Exchange connectivity.
- Exotic derivatives requiring complex path-dependent exercise.
- Production regulatory capital calculations.
- Unvalidated model calibration claims.

## Data model principles

- All request/response models must be versionable and typed.
- Use explicit units: annualized volatility, year fraction, continuous rate unless otherwise documented.
- Reject invalid inputs early with clear error messages.

## Acceptance criteria for v0.1

- Black-Scholes and Bachelier pricing implemented.
- Put-call parity test coverage.
- At least one Greek validated by closed-form vs finite-difference comparison.
- FastAPI endpoint with Pydantic request/response models.
- Full local check command passes.

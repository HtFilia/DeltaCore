# DeltaCore project specification

## Objective

Create DeltaCore: a Python backend that prices vanilla derivatives, computes Greeks, calibrates simple volatility models, and exposes risk analytics through a typed API.

## Target users

- Quant researchers who want a readable pricing sandbox.
- Quant developers who want a clean Python backend example.
- Risk analysts who need reproducible stress-testing examples.
- Recruiters or technical interviewers assessing quantitative software maturity.

## In scope

### Pricing

- European call/put under Black-Scholes.
- European call/put under Bachelier/normal model.
- Digital options as an optional later milestone.
- Monte Carlo pricing for vanilla options.

### Greeks

- Delta, gamma, vega, theta, rho.
- Closed-form Greeks where appropriate.
- Finite-difference Greeks as a generic fallback.
- Comparison tests between analytic and numerical Greeks.

### Calibration

- Implied volatility via robust root finding.
- Smile calibration to simple parametric forms as a later milestone.
- Calibration diagnostics and failure modes.

### Risk

- Scenario PnL.
- Historical or simulated VaR.
- Expected Shortfall.
- Stress testing by spot, volatility, rate, and time shocks.

### API

- `/health`
- `/price/european`
- `/greeks/european`
- `/implied-volatility`
- `/risk/scenario-pnl`
- `/risk/historical-var`
- `/demo` for a lightweight browser demonstration backed by API calls

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

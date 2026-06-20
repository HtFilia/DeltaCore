import pytest
from fastapi.testclient import TestClient

from derivatives_risk_engine.api.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_price_european_returns_black_scholes_price() -> None:
    response = client.post(
        "/price/european",
        json={
            "option_type": "call",
            "spot": 100.0,
            "strike": 100.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "dividend_yield": 0.0,
            "volatility": 0.20,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "black_scholes"
    assert payload["option_type"] == "call"
    assert payload["price"] == pytest.approx(10.450583572185565, abs=1e-12)
    assert payload["convention"] == "continuous_rates_annualized_volatility"

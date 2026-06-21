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


def test_greeks_european_returns_black_scholes_greeks() -> None:
    response = client.post(
        "/greeks/european",
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
    assert payload["delta"] == pytest.approx(0.6368306511756191, abs=1e-12)
    assert payload["gamma"] == pytest.approx(0.018762017345846895, abs=1e-12)
    assert payload["vega"] == pytest.approx(37.52403469169379, abs=1e-12)
    assert payload["theta"] == pytest.approx(-6.414027546438197, abs=1e-12)
    assert payload["rho"] == pytest.approx(53.232481545376345, abs=1e-12)
    assert payload["convention"] == "continuous_rates_annualized_volatility"


def test_implied_volatility_returns_calibration_diagnostics() -> None:
    response = client.post(
        "/implied-volatility",
        json={
            "option_type": "call",
            "spot": 100.0,
            "strike": 100.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "dividend_yield": 0.0,
            "target_price": 10.450583572185565,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "black_scholes"
    assert payload["option_type"] == "call"
    assert payload["implied_volatility"] == pytest.approx(0.20, abs=1e-12)
    assert payload["diagnostics"]["converged"] is True
    assert payload["diagnostics"]["failure_reason"] is None


def test_scenario_pnl_returns_repricing_results() -> None:
    response = client.post(
        "/risk/scenario-pnl",
        json={
            "option_type": "call",
            "spot": 100.0,
            "strike": 100.0,
            "time_to_expiry": 1.0,
            "risk_free_rate": 0.05,
            "dividend_yield": 0.0,
            "volatility": 0.20,
            "shocks": [
                {"name": "spot_down_5", "spot_shift": -5.0},
                {"name": "vol_up_5_points", "volatility_shift": 0.05},
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "black_scholes"
    assert payload["convention"] == "absolute_market_shocks"
    assert [result["scenario_name"] for result in payload["results"]] == [
        "spot_down_5",
        "vol_up_5_points",
    ]
    assert payload["results"][0]["shocked_spot"] == 95.0
    assert payload["results"][0]["pnl"] < 0.0
    assert payload["results"][1]["shocked_volatility"] == pytest.approx(0.25, abs=1e-12)
    assert payload["results"][1]["pnl"] > 0.0


def test_historical_var_endpoint_returns_var_and_expected_shortfall() -> None:
    response = client.post(
        "/risk/historical-var",
        json={
            "pnls": [12.0, 7.0, 5.0, 2.0, 0.0, -1.0, -3.0, -8.0, -10.0, -20.0],
            "confidence_level": 0.80,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["method"] == "historical"
    assert payload["confidence_level"] == 0.80
    assert payload["value_at_risk"] == pytest.approx(8.0, abs=1e-12)
    assert payload["expected_shortfall"] == pytest.approx((8.0 + 10.0 + 20.0) / 3.0, abs=1e-12)
    assert payload["num_observations"] == 10
    assert payload["tail_observations"] == 3


def test_demo_page_is_served_as_html() -> None:
    response = client.get("/demo")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "DeltaCore Demo" in response.text
    assert 'fetch("/price/european"' in response.text

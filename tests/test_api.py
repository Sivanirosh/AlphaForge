"""HTTP-level tests for the FastAPI application."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestMetricsEndpoint:
    def test_unknown_ticker_returns_404(self, client: TestClient) -> None:
        resp = client.get("/metrics/ZZZZ")
        assert resp.status_code == 404

    def test_valid_ticker_returns_200(
        self, client: TestClient, seeded_db: Session
    ) -> None:
        resp = client.get("/metrics/AAPL")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["ticker"] == "AAPL"

    def test_response_schema_fields(
        self, client: TestClient, seeded_db: Session
    ) -> None:
        resp = client.get("/metrics/AAPL")
        item = resp.json()[0]
        assert "ticker" in item
        assert "date" in item
        assert "log_return" in item


class TestBetaEndpoint:
    def test_no_beta_returns_404(
        self, client: TestClient, seeded_db: Session
    ) -> None:
        resp = client.get("/metrics/AAPL/beta")
        assert resp.status_code == 404
        assert "No beta data" in resp.json()["detail"]


class TestVolatilityEndpoint:
    def test_unknown_ticker_returns_404(self, client: TestClient) -> None:
        resp = client.get("/metrics/ZZZZ/volatility")
        assert resp.status_code == 404

    def test_valid_ticker_returns_series(
        self, client: TestClient, seeded_db: Session
    ) -> None:
        resp = client.get("/metrics/AAPL/volatility")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ticker"] == "AAPL"
        assert "series" in data

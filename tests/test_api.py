"""Integration tests for FastAPI endpoints with mocked MarketDataClient."""

from datetime import date
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from aura_pulse.api.app import app
from aura_pulse.exceptions import SymbolNotFoundError
from aura_pulse.models import (
    CompanyProfile,
    DividendEvent,
    HistoricalBar,
    HistoricalData,
    SearchResult,
    StockQuote,
    StockSplit,
)


@pytest.fixture
def mock_client():
    with patch("aura_pulse.api.app.client") as mock:
        yield mock


@pytest.fixture
async def http_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health(self, http_client):
        resp = await http_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


class TestQuoteEndpoint:
    @pytest.mark.asyncio
    async def test_success(self, http_client, mock_client):
        mock_client.get_quote.return_value = StockQuote(
            symbol="AAPL", name="Apple Inc.", price=182.52, change=1.77, change_percent=0.98
        )
        resp = await http_client.get("/api/v1/quote/AAPL")
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "AAPL"
        assert data["price"] == 182.52

    @pytest.mark.asyncio
    async def test_not_found(self, http_client, mock_client):
        mock_client.get_quote.side_effect = SymbolNotFoundError("FAKE")
        resp = await http_client.get("/api/v1/quote/FAKE")
        assert resp.status_code == 404


class TestHistoryEndpoint:
    @pytest.mark.asyncio
    async def test_success(self, http_client, mock_client):
        mock_client.get_history.return_value = HistoricalData(
            symbol="AAPL",
            period="1mo",
            interval="1d",
            bars=[HistoricalBar(date=date(2024, 1, 15), open=150, high=155, low=149, close=153, volume=1_000_000)],
        )
        resp = await http_client.get("/api/v1/history/AAPL?period=1mo&interval=1d")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["bars"]) == 1


class TestProfileEndpoint:
    @pytest.mark.asyncio
    async def test_success(self, http_client, mock_client):
        mock_client.get_company_profile.return_value = CompanyProfile(
            symbol="AAPL", name="Apple Inc.", sector="Technology"
        )
        resp = await http_client.get("/api/v1/profile/AAPL")
        assert resp.status_code == 200
        data = resp.json()
        assert data["sector"] == "Technology"


class TestDividendsEndpoint:
    @pytest.mark.asyncio
    async def test_success(self, http_client, mock_client):
        mock_client.get_dividends.return_value = [DividendEvent(date=date(2024, 2, 9), amount=0.24)]
        resp = await http_client.get("/api/v1/dividends/AAPL")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["amount"] == 0.24


class TestSplitsEndpoint:
    @pytest.mark.asyncio
    async def test_success(self, http_client, mock_client):
        mock_client.get_splits.return_value = [StockSplit(date=date(2020, 8, 31), ratio="4:1")]
        resp = await http_client.get("/api/v1/splits/AAPL")
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["ratio"] == "4:1"


class TestSearchEndpoint:
    @pytest.mark.asyncio
    async def test_success(self, http_client, mock_client):
        mock_client.search.return_value = [
            SearchResult(symbol="AAPL", name="Apple Inc.", exchange="NMS", asset_type="EQUITY")
        ]
        resp = await http_client.get("/api/v1/search?q=apple")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"

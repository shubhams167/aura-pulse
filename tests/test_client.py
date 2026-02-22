"""Tests for MarketDataClient using mocked yfinance responses."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from api.client import MarketDataClient
from api.exceptions import SymbolNotFoundError


@pytest.fixture
def client():
    return MarketDataClient()


# --------------------------------------------------------------------------
# Fixtures — mock yfinance data
# --------------------------------------------------------------------------

MOCK_INFO = {
    "shortName": "Apple Inc.",
    "longName": "Apple Inc.",
    "currentPrice": 182.52,
    "previousClose": 180.75,
    "open": 181.0,
    "dayHigh": 183.0,
    "dayLow": 180.0,
    "volume": 55_000_000,
    "marketCap": 2_800_000_000_000,
    "currency": "USD",
    "exchange": "NMS",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones...",
    "website": "https://www.apple.com",
    "country": "United States",
    "fullTimeEmployees": 164_000,
    "trailingPE": 28.5,
    "forwardPE": 26.1,
    "dividendYield": 0.005,
    "beta": 1.25,
    "fiftyTwoWeekHigh": 199.62,
    "fiftyTwoWeekLow": 143.90,
}


def _mock_history_df():
    dates = pd.to_datetime(["2024-01-15", "2024-01-16", "2024-01-17"])
    return pd.DataFrame(
        {
            "Open": [150.0, 153.0, 155.0],
            "High": [155.0, 157.0, 158.0],
            "Low": [149.0, 152.0, 154.0],
            "Close": [153.0, 156.0, 157.5],
            "Volume": [1_000_000, 1_200_000, 1_100_000],
        },
        index=dates,
    )


def _mock_dividends():
    dates = pd.to_datetime(["2024-02-09", "2024-05-10"])
    return pd.Series([0.24, 0.25], index=dates, name="Dividends")


def _mock_splits():
    dates = pd.to_datetime(["2020-08-31"])
    return pd.Series([4.0], index=dates, name="Stock Splits")


def _mock_financials():
    dates = pd.to_datetime(["2024-09-30", "2023-09-30"])
    return pd.DataFrame(
        {
            dates[0]: [94_930_000_000, 14_736_000_000],
            dates[1]: [89_500_000_000, 12_580_000_000],
        },
        index=["Total Revenue", "Net Income"],
    )


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


class TestGetQuote:
    @patch("api.client.yf.Ticker")
    def test_success(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.info = MOCK_INFO
        mock_ticker_cls.return_value = mock_ticker

        quote = client.get_quote("AAPL")

        assert quote.symbol == "AAPL"
        assert quote.name == "Apple Inc."
        assert quote.price == 182.52
        assert quote.change == round(182.52 - 180.75, 4)
        assert quote.currency == "USD"

    @patch("api.client.yf.Ticker")
    def test_symbol_not_found(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker_cls.return_value = mock_ticker

        with pytest.raises(SymbolNotFoundError):
            client.get_quote("FAKESYMBOL")

    def test_empty_symbol(self, client):
        with pytest.raises(SymbolNotFoundError):
            client.get_quote("")


class TestGetHistory:
    @patch("api.client.yf.Ticker")
    def test_success(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = _mock_history_df()
        mock_ticker.info = {"currency": "USD"}
        mock_ticker_cls.return_value = mock_ticker

        history = client.get_history("AAPL", period="1mo", interval="1d")

        assert history.symbol == "AAPL"
        assert len(history.bars) == 3
        assert history.bars[0].close == 153.0
        assert history.bars[1].volume == 1_200_000

    @patch("api.client.yf.Ticker")
    def test_empty_history(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker

        with pytest.raises(SymbolNotFoundError):
            client.get_history("FAKESYMBOL")


class TestGetCompanyProfile:
    @patch("api.client.yf.Ticker")
    def test_success(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.info = MOCK_INFO
        mock_ticker_cls.return_value = mock_ticker

        profile = client.get_company_profile("AAPL")

        assert profile.name == "Apple Inc."
        assert profile.sector == "Technology"
        assert profile.industry == "Consumer Electronics"
        assert profile.pe_ratio == 28.5

    @patch("api.client.yf.Ticker")
    def test_not_found(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker_cls.return_value = mock_ticker

        with pytest.raises(SymbolNotFoundError):
            client.get_company_profile("FAKESYMBOL")


class TestGetFinancials:
    @patch("api.client.yf.Ticker")
    def test_income_statement(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.financials = _mock_financials()
        mock_ticker_cls.return_value = mock_ticker

        statements = client.get_financials("AAPL", statement="income")

        assert len(statements) == 2
        assert statements[0].data["Total Revenue"] == 94_930_000_000

    @patch("api.client.yf.Ticker")
    def test_empty_financials(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.financials = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker

        result = client.get_financials("AAPL")
        assert result == []


class TestGetDividends:
    @patch("api.client.yf.Ticker")
    def test_success(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.dividends = _mock_dividends()
        mock_ticker_cls.return_value = mock_ticker

        dividends = client.get_dividends("AAPL")

        assert len(dividends) == 2
        assert dividends[0].amount == 0.24


class TestGetSplits:
    @patch("api.client.yf.Ticker")
    def test_success(self, mock_ticker_cls, client):
        mock_ticker = MagicMock()
        mock_ticker.splits = _mock_splits()
        mock_ticker_cls.return_value = mock_ticker

        splits = client.get_splits("AAPL")

        assert len(splits) == 1
        assert splits[0].ratio == "4:1"


class TestFormatSplitRatio:
    def test_forward_split(self):
        assert MarketDataClient._format_split_ratio(4.0) == "4:1"

    def test_reverse_split(self):
        assert MarketDataClient._format_split_ratio(0.5) == "1:2"

    def test_one_to_one(self):
        assert MarketDataClient._format_split_ratio(1.0) == "1:1"

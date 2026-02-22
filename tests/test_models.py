"""Tests for Pydantic models."""

from datetime import date

from api.models import (
    CompanyProfile,
    DividendEvent,
    FinancialStatement,
    HistoricalBar,
    HistoricalData,
    SearchResult,
    StockQuote,
    StockSplit,
)


class TestStockQuote:
    def test_minimal_creation(self):
        q = StockQuote(symbol="AAPL", price=150.0)
        assert q.symbol == "AAPL"
        assert q.price == 150.0
        assert q.change == 0.0
        assert q.currency == "USD"

    def test_full_creation(self):
        q = StockQuote(
            symbol="AAPL",
            name="Apple Inc.",
            price=150.25,
            previous_close=148.50,
            open=149.0,
            day_high=151.0,
            day_low=148.0,
            change=1.75,
            change_percent=1.18,
            volume=50_000_000,
            market_cap=2_500_000_000_000,
            currency="USD",
            exchange="NMS",
        )
        assert q.name == "Apple Inc."
        assert q.change_percent == 1.18

    def test_serialization(self):
        q = StockQuote(symbol="TSLA", price=200.0)
        data = q.model_dump()
        assert data["symbol"] == "TSLA"
        assert "timestamp" in data


class TestHistoricalBar:
    def test_creation(self):
        bar = HistoricalBar(
            date=date(2024, 1, 15),
            open=150.0,
            high=155.0,
            low=149.0,
            close=153.0,
            volume=1_000_000,
        )
        assert bar.date == date(2024, 1, 15)
        assert bar.close == 153.0


class TestHistoricalData:
    def test_creation_with_bars(self):
        bars = [
            HistoricalBar(date=date(2024, 1, 15), open=150, high=155, low=149, close=153, volume=1_000_000),
            HistoricalBar(date=date(2024, 1, 16), open=153, high=157, low=152, close=156, volume=1_200_000),
        ]
        hd = HistoricalData(symbol="AAPL", period="1mo", interval="1d", bars=bars)
        assert len(hd.bars) == 2
        assert hd.period == "1mo"

    def test_empty_bars(self):
        hd = HistoricalData(symbol="AAPL", period="1mo", interval="1d", bars=[])
        assert len(hd.bars) == 0


class TestCompanyProfile:
    def test_minimal(self):
        p = CompanyProfile(symbol="AAPL")
        assert p.symbol == "AAPL"
        assert p.name is None

    def test_full(self):
        p = CompanyProfile(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            market_cap=2_500_000_000_000,
            pe_ratio=28.5,
        )
        assert p.sector == "Technology"


class TestFinancialStatement:
    def test_creation(self):
        fs = FinancialStatement(
            period_ending=date(2024, 9, 30),
            data={"Total Revenue": 94_930_000_000, "Net Income": 14_736_000_000},
        )
        assert fs.period_ending == date(2024, 9, 30)
        assert fs.data["Total Revenue"] == 94_930_000_000


class TestDividendEvent:
    def test_creation(self):
        d = DividendEvent(date=date(2024, 2, 9), amount=0.24)
        assert d.amount == 0.24


class TestStockSplit:
    def test_creation(self):
        s = StockSplit(date=date(2020, 8, 31), ratio="4:1")
        assert s.ratio == "4:1"


class TestSearchResult:
    def test_creation(self):
        sr = SearchResult(symbol="AAPL", name="Apple Inc.", exchange="NMS", asset_type="EQUITY")
        assert sr.symbol == "AAPL"
        assert sr.asset_type == "EQUITY"

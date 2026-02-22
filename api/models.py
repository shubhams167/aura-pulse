"""Pydantic models for market data responses."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class StockQuote(BaseModel):
    """Current price snapshot for a stock."""

    symbol: str
    name: str | None = None
    price: float
    previous_close: float | None = None
    open: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    change: float = 0.0
    change_percent: float = 0.0
    volume: int | None = None
    market_cap: int | None = None
    currency: str = "USD"
    exchange: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HistoricalBar(BaseModel):
    """A single OHLCV bar."""

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoricalData(BaseModel):
    """Historical price data with metadata."""

    symbol: str
    period: str
    interval: str
    bars: list[HistoricalBar]
    currency: str = "USD"


class CompanyProfile(BaseModel):
    """Company information and fundamentals."""

    symbol: str
    name: str | None = None
    sector: str | None = None
    industry: str | None = None
    description: str | None = None
    website: str | None = None
    country: str | None = None
    employees: int | None = None
    market_cap: int | None = None
    pe_ratio: float | None = None
    forward_pe: float | None = None
    dividend_yield: float | None = None
    beta: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None


class FinancialStatement(BaseModel):
    """A row in a financial statement (income / balance sheet / cash flow)."""

    period_ending: date
    data: dict[str, float | None]


class DividendEvent(BaseModel):
    """A single dividend payment."""

    date: date
    amount: float


class StockSplit(BaseModel):
    """A stock split event."""

    date: date
    ratio: str


class SearchResult(BaseModel):
    """A search result for a ticker query."""

    symbol: str
    name: str | None = None
    exchange: str | None = None
    asset_type: str | None = None

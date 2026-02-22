"""aura-pulse — A clean, typed Python wrapper around yfinance."""

from api.client import MarketDataClient
from api.exceptions import MarketDataError, RateLimitError, SymbolNotFoundError
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

__all__ = [
    "MarketDataClient",
    "MarketDataError",
    "RateLimitError",
    "SymbolNotFoundError",
    "CompanyProfile",
    "DividendEvent",
    "FinancialStatement",
    "HistoricalBar",
    "HistoricalData",
    "SearchResult",
    "StockQuote",
    "StockSplit",
]

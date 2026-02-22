"""aura-pulse — A clean, typed Python wrapper around yfinance."""

from .client import MarketDataClient
from .exceptions import MarketDataError, RateLimitError, SymbolNotFoundError
from .models import (
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

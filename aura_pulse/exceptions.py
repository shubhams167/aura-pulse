"""Custom exceptions for aura-pulse."""


class MarketDataError(Exception):
    """Base exception for all market data errors."""

    def __init__(self, message: str, symbol: str | None = None):
        self.symbol = symbol
        super().__init__(message)


class SymbolNotFoundError(MarketDataError):
    """Raised when a ticker symbol cannot be found."""

    def __init__(self, symbol: str):
        super().__init__(f"Symbol not found: {symbol}", symbol=symbol)


class RateLimitError(MarketDataError):
    """Raised when Yahoo Finance rate-limits the request."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message)

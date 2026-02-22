"""FastAPI application exposing market data endpoints.

This is the main entrypoint for both Vercel serverless deployment
and the local CLI dev-server.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
load_dotenv()

from .client import MarketDataClient
from .exceptions import MarketDataError, SymbolNotFoundError
from .models import (
    CompanyProfile,
    DividendEvent,
    FinancialStatement,
    HistoricalData,
    SearchResult,
    StockQuote,
    StockSplit,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Aura Pulse",
    description="A clean REST API for stock market data, powered by yfinance.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MarketDataClient()


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------


@app.exception_handler(SymbolNotFoundError)
async def symbol_not_found_handler(_request, exc: SymbolNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(MarketDataError)
async def market_data_error_handler(_request, exc: MarketDataError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "aura-pulse"}


@app.get("/api/v1/quote/{symbol}", response_model=StockQuote)
async def get_quote(symbol: str):
    """Get the current price quote for a stock."""
    try:
        return client.get_quote(symbol)
    except SymbolNotFoundError:
        raise
    except Exception as exc:
        logger.exception("Error fetching quote for %s", symbol)
        raise HTTPException(status_code=500, detail=f"Failed to fetch quote: {exc}") from exc


@app.get("/api/v1/history/{symbol}", response_model=HistoricalData)
async def get_history(
    symbol: str,
    period: Annotated[str, Query(description="1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")] = "1mo",
    interval: Annotated[str, Query(description="1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")] = "1d",
):
    """Get historical OHLCV data for a stock."""
    try:
        return client.get_history(symbol, period=period, interval=interval)
    except SymbolNotFoundError:
        raise
    except Exception as exc:
        logger.exception("Error fetching history for %s", symbol)
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {exc}") from exc


@app.get("/api/v1/profile/{symbol}", response_model=CompanyProfile)
async def get_profile(symbol: str):
    """Get the company profile and fundamentals for a stock."""
    try:
        return client.get_company_profile(symbol)
    except SymbolNotFoundError:
        raise
    except Exception as exc:
        logger.exception("Error fetching profile for %s", symbol)
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {exc}") from exc


@app.get("/api/v1/financials/{symbol}", response_model=list[FinancialStatement])
async def get_financials(
    symbol: str,
    statement: Annotated[str, Query(description="income, balance, or cashflow")] = "income",
):
    """Get financial statements for a stock."""
    try:
        return client.get_financials(symbol, statement=statement)
    except (SymbolNotFoundError, MarketDataError):
        raise
    except Exception as exc:
        logger.exception("Error fetching financials for %s", symbol)
        raise HTTPException(status_code=500, detail=f"Failed to fetch financials: {exc}") from exc


@app.get("/api/v1/dividends/{symbol}", response_model=list[DividendEvent])
async def get_dividends(symbol: str):
    """Get dividend history for a stock."""
    try:
        return client.get_dividends(symbol)
    except SymbolNotFoundError:
        raise
    except Exception as exc:
        logger.exception("Error fetching dividends for %s", symbol)
        raise HTTPException(status_code=500, detail=f"Failed to fetch dividends: {exc}") from exc


@app.get("/api/v1/splits/{symbol}", response_model=list[StockSplit])
async def get_splits(symbol: str):
    """Get stock split history for a stock."""
    try:
        return client.get_splits(symbol)
    except SymbolNotFoundError:
        raise
    except Exception as exc:
        logger.exception("Error fetching splits for %s", symbol)
        raise HTTPException(status_code=500, detail=f"Failed to fetch splits: {exc}") from exc


@app.get("/api/v1/search", response_model=list[SearchResult])
async def search_tickers(
    q: Annotated[str, Query(description="Search query (company name or ticker)")],
    max_results: Annotated[int, Query(ge=1, le=50)] = 10,
):
    """Search for tickers matching a query."""
    return client.search(q, max_results=max_results)


@app.get("/api/v1/trending", response_model=list[SearchResult])
async def get_trending():
    """Get a list of currently trending tickers."""
    try:
        return client.get_trending_tickers()
    except Exception as exc:
        logger.exception("Error fetching trending tickers")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending: {exc}") from exc


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    """Run the API server via ``aura-pulse`` CLI command."""
    import uvicorn

    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()


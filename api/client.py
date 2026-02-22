"""MarketDataClient — typed wrapper around yfinance."""

from __future__ import annotations

import logging
from datetime import datetime

import yfinance as yf

from .exceptions import MarketDataError, SymbolNotFoundError
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

logger = logging.getLogger(__name__)


class MarketDataClient:
    """A clean, typed wrapper around yfinance for fetching market data.

    Usage::

        client = MarketDataClient()
        quote = client.get_quote("AAPL")
        print(f"{quote.symbol}: ${quote.price:.2f}")
    """

    # ------------------------------------------------------------------
    # Quotes
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_logo_urls(symbol: str, website: str | None) -> tuple[str | None, str | None]:
        """Helper to construct Logo API URLs (Ticker prioritizing over Domain)."""
        import os
        token = os.environ.get("LOGO_DEV_TOKEN")
        if not token:
            return None, None
            
        ticker_url = f"https://img.logo.dev/ticker/{symbol}?token={token}&size=80"
        
        domain_url = None
        if website:
            import urllib.parse
            parsed = urllib.parse.urlparse(website)
            domain = parsed.netloc if parsed.netloc else parsed.path
            if domain.startswith("www."):
                domain = domain[4:]
            if domain:
                domain_url = f"https://img.logo.dev/{domain}?token={token}&size=80"
        
        return ticker_url, domain_url

    def get_quote(self, symbol: str) -> StockQuote:
        """Fetch the current price quote for *symbol*."""
        ticker = self._get_ticker(symbol)
        info = ticker.info

        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            raise SymbolNotFoundError(symbol)

        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        change = (price - prev_close) if prev_close else 0.0
        change_pct = (change / prev_close * 100) if prev_close else 0.0

        website = info.get("website")
        logo_url, domain_url = self._extract_logo_urls(symbol, website)

        return StockQuote(
            symbol=symbol.upper(),
            name=info.get("shortName") or info.get("longName"),
            price=price,
            previous_close=prev_close,
            open=info.get("open") or info.get("regularMarketOpen"),
            day_high=info.get("dayHigh") or info.get("regularMarketDayHigh"),
            day_low=info.get("dayLow") or info.get("regularMarketDayLow"),
            change=round(change, 4),
            change_percent=round(change_pct, 4),
            volume=info.get("volume") or info.get("regularMarketVolume"),
            market_cap=info.get("marketCap"),
            currency=info.get("currency", "USD"),
            exchange=info.get("exchange"),
            logo_url=logo_url,
            domain_url=domain_url,
        )

    # ------------------------------------------------------------------
    # Historical data
    # ------------------------------------------------------------------

    def get_history(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
    ) -> HistoricalData:
        """Fetch historical OHLCV bars for *symbol*.

        Args:
            symbol: Ticker symbol (e.g. ``"AAPL"``).
            period: Data period — ``1d``, ``5d``, ``1mo``, ``3mo``, ``6mo``,
                ``1y``, ``2y``, ``5y``, ``10y``, ``ytd``, ``max``.
            interval: Bar interval — ``1m``, ``2m``, ``5m``, ``15m``, ``30m``,
                ``60m``, ``90m``, ``1h``, ``1d``, ``5d``, ``1wk``, ``1mo``, ``3mo``.
        """
        ticker = self._get_ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            raise SymbolNotFoundError(symbol)

        bars: list[HistoricalBar] = []
        for idx, row in df.iterrows():
            bar_date = idx.date() if isinstance(idx, (datetime,)) else idx
            bars.append(
                HistoricalBar(
                    date=bar_date,
                    open=round(row["Open"], 4),
                    high=round(row["High"], 4),
                    low=round(row["Low"], 4),
                    close=round(row["Close"], 4),
                    volume=int(row["Volume"]),
                )
            )

        info = ticker.info
        return HistoricalData(
            symbol=symbol.upper(),
            period=period,
            interval=interval,
            bars=bars,
            currency=info.get("currency", "USD"),
        )

    # ------------------------------------------------------------------
    # Company profile
    # ------------------------------------------------------------------

    def get_company_profile(self, symbol: str) -> CompanyProfile:
        """Fetch the company profile / fundamentals for *symbol*."""
        ticker = self._get_ticker(symbol)
        info = ticker.info

        if not info.get("shortName") and not info.get("longName"):
            raise SymbolNotFoundError(symbol)

        website = info.get("website")
        logo_url, domain_url = self._extract_logo_urls(symbol, website)

        return CompanyProfile(
            symbol=symbol.upper(),
            name=info.get("shortName") or info.get("longName"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            description=info.get("longBusinessSummary"),
            website=website,
            country=info.get("country"),
            employees=info.get("fullTimeEmployees"),
            logo_url=logo_url,
            domain_url=domain_url,
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            forward_pe=info.get("forwardPE"),
            dividend_yield=info.get("dividendYield"),
            beta=info.get("beta"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            currency=info.get("currency", "USD"),
        )

    # ------------------------------------------------------------------
    # Financial statements
    # ------------------------------------------------------------------

    def get_financials(
        self,
        symbol: str,
        statement: str = "income",
    ) -> list[FinancialStatement]:
        """Fetch financial statements for *symbol*.

        Args:
            statement: One of ``income``, ``balance``, ``cashflow``.
        """
        ticker = self._get_ticker(symbol)

        match statement:
            case "income":
                df = ticker.financials
            case "balance":
                df = ticker.balance_sheet
            case "cashflow":
                df = ticker.cashflow
            case _:
                raise MarketDataError(
                    f"Invalid statement type: {statement!r}. Use 'income', 'balance', or 'cashflow'.",
                    symbol=symbol,
                )

        if df is None or df.empty:
            return []

        results: list[FinancialStatement] = []
        for col in df.columns:
            period_date = col.date() if isinstance(col, (datetime,)) else col
            data = {str(k): (float(v) if v == v else None) for k, v in df[col].items()}  # NaN check via v == v
            results.append(FinancialStatement(period_ending=period_date, data=data))

        return results

    # ------------------------------------------------------------------
    # Dividends
    # ------------------------------------------------------------------

    def get_dividends(self, symbol: str) -> list[DividendEvent]:
        """Fetch dividend history for *symbol*."""
        ticker = self._get_ticker(symbol)
        divs = ticker.dividends

        if divs is None or divs.empty:
            return []

        return [
            DividendEvent(date=idx.date() if isinstance(idx, datetime) else idx, amount=round(float(val), 6))
            for idx, val in divs.items()
        ]

    # ------------------------------------------------------------------
    # Splits
    # ------------------------------------------------------------------

    def get_splits(self, symbol: str) -> list[StockSplit]:
        """Fetch stock-split history for *symbol*."""
        ticker = self._get_ticker(symbol)
        splits = ticker.splits

        if splits is None or splits.empty:
            return []

        return [
            StockSplit(
                date=idx.date() if isinstance(idx, datetime) else idx,
                ratio=self._format_split_ratio(float(val)),
            )
            for idx, val in splits.items()
        ]

    # ------------------------------------------------------------------
    # Search & Trending
    # ------------------------------------------------------------------

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search Yahoo Finance for tickers matching *query*."""
        try:
            results = yf.Search(query)
            quotes = results.quotes if hasattr(results, "quotes") else []
        except Exception as exc:
            logger.warning("Search failed for %r: %s", query, exc)
            return []

        search_results: list[SearchResult] = []
        for q in quotes[:max_results]:
            sym = q.get("symbol", "")
            # Since search doesn't provide website, we only get ticker URL
            logo_url, domain_url = self._extract_logo_urls(sym, None)
            search_results.append(
                SearchResult(
                    symbol=sym,
                    name=q.get("shortname") or q.get("longname"),
                    exchange=q.get("exchange"),
                    asset_type=q.get("quoteType"),
                    logo_url=logo_url,
                    domain_url=domain_url,
                    currency=q.get("currency", "USD"),
                )
            )

        return search_results

    def get_trending_tickers(self) -> list[SearchResult]:
        """Fetch currently trending tickers from Yahoo Finance or use a fallback list."""
        try:
            # We'll use a hardcoded list of major popular tech and market index ETF tickers 
            # to simulate 'trending' if yf doesn't easily expose a dedicated list.
            # In a real app we might scrape Yahoo's trending page or use a specific API.
            popular_symbols = ["NVDA", "TSLA", "AAPL", "AMD", "META", "AMZN", "MSFT", "GOOGL", "QQQ", "SPY"]
            
            tickers = yf.Tickers(" ".join(popular_symbols))
            results: list[SearchResult] = []
            
            for sym in popular_symbols:
                try:
                    q = tickers.tickers[sym].info
                    logo_url, domain_url = self._extract_logo_urls(sym, q.get("website"))
                    results.append(
                        SearchResult(
                            symbol=sym,
                            name=q.get("shortName") or q.get("longName"),
                            exchange=q.get("exchange"),
                            asset_type=q.get("quoteType"),
                            logo_url=logo_url,
                            domain_url=domain_url,
                            currency=q.get("currency", "USD"),
                        )
                    )
                except Exception:
                    pass
            
            return results
        except Exception as exc:
            logger.warning("Trending fetch failed: %s", exc)
            return []


    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_ticker(symbol: str) -> yf.Ticker:
        """Create a yfinance Ticker, raising on obviously bad symbols."""
        if not symbol or not symbol.strip():
            raise SymbolNotFoundError(symbol)
        return yf.Ticker(symbol.strip().upper())

    @staticmethod
    def _format_split_ratio(ratio: float) -> str:
        """Convert a numeric split ratio like 4.0 to ``'4:1'``."""
        if ratio >= 1:
            return f"{int(ratio)}:1"
        inverse = 1 / ratio
        return f"1:{int(inverse)}"

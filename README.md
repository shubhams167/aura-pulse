# aura-pulse

A clean, typed Python wrapper around [yfinance](https://github.com/ranaroussi/yfinance) for fetching stock market data — usable as a **Python library** or as a **REST API** via FastAPI.

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd aura-pulse

# Install dependencies
uv sync --all-extras
```

### Use as a Python library

```python
from api.client import MarketDataClient

client = MarketDataClient()

# Get a live quote
quote = client.get_quote("AAPL")
print(f"{quote.symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")

# Get historical data
history = client.get_history("MSFT", period="3mo", interval="1d")
for bar in history.bars[:3]:
    print(f"  {bar.date}  O:{bar.open:.2f}  H:{bar.high:.2f}  L:{bar.low:.2f}  C:{bar.close:.2f}")

# Company profile
profile = client.get_company_profile("GOOGL")
print(f"{profile.name} — {profile.sector} / {profile.industry}")
```

### Run the REST API

```bash
uv run uvicorn api.index:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

#### Example endpoints

| Method | Endpoint | Description |
|--------|-------------------------------|--------------------------|
| GET | `/api/v1/quote/{symbol}` | Current price quote |
| GET | `/api/v1/history/{symbol}` | Historical OHLCV bars |
| GET | `/api/v1/profile/{symbol}` | Company profile |
| GET | `/api/v1/financials/{symbol}` | Financial statements |
| GET | `/api/v1/dividends/{symbol}` | Dividend history |
| GET | `/api/v1/splits/{symbol}` | Stock split history |
| GET | `/api/v1/search?q=...` | Search for tickers |
| GET | `/health` | Health check |

### Development

```bash
# Run tests
uv run pytest -v

# Lint & format
uv run ruff check .
uv run ruff format .
```

## License

MIT

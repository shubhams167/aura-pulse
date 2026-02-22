# aura-pulse

A clean REST API for stock market data, powered by [yfinance](https://github.com/ranaroussi/yfinance) and [FastAPI](https://fastapi.tiangolo.com/). Designed for deployment on **Vercel** as a serverless Python function.

## Project Structure

```
aura-pulse/
├── api/
│   ├── index.py        ← FastAPI app (Vercel entrypoint)
│   ├── client.py       ← MarketDataClient (yfinance wrapper)
│   ├── models.py       ← Pydantic response models
│   └── exceptions.py   ← Custom exceptions
├── tests/
├── vercel.json         ← Routes all traffic to api/index.py
├── requirements.txt    ← For Vercel's pip install
└── pyproject.toml
```

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
git clone https://github.com/shubhams167/aura-pulse.git
cd aura-pulse
uv sync --all-extras
```

### Run Locally

```bash
uv run aura-pulse
```

The API will be available at [http://localhost:8000](http://localhost:8000).
Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

### Deploy to Vercel

1. Import the repo on [Vercel](https://vercel.com/new).
2. Deploy — Vercel auto-detects the Python runtime via `requirements.txt` and `vercel.json`.

## API Endpoints

| Method | Endpoint                      | Description              |
|--------|-------------------------------|--------------------------|
| GET    | `/`                           | Health check             |
| GET    | `/api/v1/quote/{symbol}`      | Current price quote      |
| GET    | `/api/v1/history/{symbol}`    | Historical OHLCV bars    |
| GET    | `/api/v1/profile/{symbol}`    | Company profile          |
| GET    | `/api/v1/financials/{symbol}` | Financial statements     |
| GET    | `/api/v1/dividends/{symbol}`  | Dividend history         |
| GET    | `/api/v1/splits/{symbol}`     | Stock split history      |
| GET    | `/api/v1/search?q=...`        | Search for tickers       |

## Development

```bash
# Run tests
uv run python -m pytest -v

# Lint & format
uv run ruff check .
uv run ruff format .
```

## License

MIT

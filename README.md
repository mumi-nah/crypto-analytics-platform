# 📊 Crypto Market Data Pipeline + Analytics API

A production-style data engineering system that ingests near real-time cryptocurrency market data, stores, computes analytics, and serves clean cryptocurrency market data via a REST API.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
  - [With Docker](#with-docker)
  - [Running the Pipeline](#running-the-pipeline)
  - [Database Migrations](#database-migrations)
- [Scheduling](#scheduling)
- [API Reference](#api-reference)
  - [Health](#health)
  - [Prices](#prices)
  - [Metrics](#metrics)
  - [Signals](#signals)
  - [Pipeline Control](#pipeline-control)
- [Supported Coins](#supported-coins)
- [Data Flow](#data-flow)
- [Database Schema](#database-schema)
- [Analytics](#analytics)
- [Design Decisions](#design-decisions)
- [Future Improvements](#future-improvements)

---

## 🚀 Overview

Investors and traders need access to timely, processed financial data to make decisions. Raw market data is noisy and not directly useful.

This project solves that by:

- Ingesting OHLC (Open, High, Low, Close) market data from the CoinGecko API
- Transforming and storing it in a structured PostgreSQL database
- Applies incremental loading to avoid duplicate ingestion
- Computing analytics indicators (moving average, volatility)
- Exposing all data via a FastAPI backend with clear, documented endpoints
- Running automatically on a weekly cron schedule
- Is fully containerized using Docker

---

## 🧠 Architecture

![Architecture flow](Images/flow.svg)

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Data Processing | Pandas |
| HTTP Client | Requests |
| Containerisation | Docker + Docker Compose |
| Package Manager | uv (Astral) |
| Scheduling | Linux cron |

---

## 📂 Project Structure

```
market-data-pipeline/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── metrics.py        # analytics + signal routes
│   │   ├── pipeline.py       # pipeline control routes
│   │   └── prices.py         # price data routes
│   ├── db/
│   │   ├── base.py           # SQLAlchemy declarative base
│   │   └── session.py        # DB engine + session factory
│   ├── models/
│   │   └── prices.py         # ORM table definitions
│   ├── schemas/
│   │   └── prices.py         # Pydantic request/response schemas
│   ├── services/
│   │   └── prices.py         # database query logic
│   └── main.py               # FastAPI app entry point
├── pipeline/
│   ├── __init__.py
│   ├── fetch.py              # ingest + transform + load to DB
│   └── metrics.py          # compute + save processed metrics
├── alembic/
│   ├── versions/             # migration scripts
│   └── env.py
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- Python 3.12+

### Installation

```bash
# Clone the repository
git clone https://github.com/mumi-nah/market-data-pipeline.git
cd market-data-pipeline

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### Environment Variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

```env
# .env.example

# Used by terminal scripts (alembic, pipeline)
DATABASE_URL=postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/marketdata

# PostgreSQL container credentials
POSTGRES_USER=YOUR_USER
POSTGRES_PASSWORD=YOUR_PASSWORD
POSTGRES_DB=marketdata

# CoinGecko API key (free demo key from https://www.coingecko.com/en/api)
API_KEY=your_api_key_here

```

---

## 🐳 Running the Project

### With Docker

```bash
# Start both the API and database containers
docker compose up --build -d

# Check containers are running
docker ps
```

The API will be available at `http://localhost:8000`.
Interactive API docs at `http://localhost:8000/docs`.

To stop:

```bash
docker compose down
```

### Database Migrations

Run inside the api container after first startup:

```bash
docker exec -it api_con alembic upgrade head
```

Or from your terminal (requires Docker DB to be running):

```bash
PYTHONPATH=$(pwd) alembic upgrade head
```

### Running the Pipeline

Load initial data into the database:

```bash
# Fetch and store raw OHLC data
docker exec -it api_con python -m pipeline.fetch

# Compute and store analytics
docker exec -it api_con python -m pipeline.analytics
```

Verify data loaded correctly:

```bash
docker exec -it <db_container_name> psql -U YOUR_USER -d marketdata \
  -c "SELECT symbol, COUNT(*) FROM raw_prices GROUP BY symbol;"
```

---

## ⏱ Scheduling (Weekly Automation)

The pipeline runs automatically via a **Linux cron job** once a week to fetch new candle data and recompute metrics.

To set up the cron job:

```bash
crontab -e
```

Add the following line to run every Monday at 2am:

```
0 2 * * 1 cd /path/to/market-data-pipeline && docker exec api_con python -m pipeline.fetch && docker exec api_con python -m pipeline.metrics >> /var/log/market-pipeline.log 2>&1
```

---

## API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

### Health

#### `GET /health`

Returns API status.

**Response**
```json
{ "status": "ok" }
```

---

### Prices

#### `GET /prices/latest`

Returns the most recent price entry for a coin.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | ✅ | Coin symbol in uppercase e.g. `BITCOIN` |

**Example**
```
GET /prices/latest?symbol=BITCOIN
```

**Response**
```json
{
  "symbol": "BITCOIN",
  "close": 63420.5,
  "timestamp": "2026-04-21T00:00:00"
}
```

---

#### `GET /prices/history/range`

Returns paginated OHLC price history within a date range.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | ✅ | Coin symbol in uppercase |
| `start` | datetime | ✅ | Start date — format: `YYYY-MM-DDTHH:MM:SS` |
| `end` | datetime | ✅ | End date — format: `YYYY-MM-DDTHH:MM:SS` |
| `limit` | integer | ❌ | Rows to return (default: 100, max: 1000) |
| `offset` | integer | ❌ | Rows to skip for pagination (default: 0) |

**Example**
```
GET /prices/history/range?symbol=BITCOIN&start=2025-01-01T00:00:00&end=2025-06-01T00:00:00
```

---

#### `GET /prices/hloc`

Returns OHLC candlestick data for a coin within a date range.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | ✅ | Coin symbol in uppercase |
| `start` | datetime | ✅ | Start date — format: `YYYY-MM-DDTHH:MM:SS` |
| `end` | datetime | ✅ | End date — format: `YYYY-MM-DDTHH:MM:SS` |

**Example**
```
GET /prices/hloc?symbol=ETHEREUM&start=2025-01-01T00:00:00&end=2025-04-01T00:00:00
```

**Response**
```json
[
  {
    "symbol": "ETHEREUM",
    "open": 3200.1,
    "high": 3450.0,
    "low": 3180.5,
    "close": 3380.2,
    "timestamp": "2025-01-01T00:00:00"
  }
]
```

---

### Metrics

#### `GET /metrics/{symbol}`

Returns the latest computed analytics for a coin.

**Path Parameters**

| Parameter | Type | Description |
|---|---|---|
| `symbol` | string | Coin symbol in uppercase e.g. `BITCOIN` |

**Example**
```
GET /metrics/BITCOIN
```

**Response**
```json
{
  "symbol": "BITCOIN",
  "moving_avg": 61500.42,
  "volatility": 2340.18,
  "timestamp": "2026-04-21T00:00:00"
}
```

---

### Signals

#### `GET /metrics/signals/{symbol}`

Returns a BUY, SELL, or HOLD signal based on comparing the latest close price against the moving average.

**Signal logic:**
- `BUY` — latest close price is above the moving average
- `SELL` — latest close price is below the moving average
- `HOLD` — latest close price equals the moving average

**Example**
```
GET /metrics/signals/BITCOIN
```

**Response**
```json
{
  "symbol": "BITCOIN",
  "signal": "BUY",
  "close": 63420.5,
  "moving_avg": 61500.42,
  "timestamp": "2026-04-21T00:00:00"
}
```

---

### Pipeline Control

#### `POST /pipeline/ingest`

Manually triggers a data ingestion job for a specific coin.

**Request Body**
```json
{ "symbol": "bitcoin" }
```

**Response**
```json
{
  "symbol": "bitcoin",
  "status": "success",
  "rows_inserted": 92
}
```

---

## Supported Coins

All symbol parameters must be passed in **uppercase**.

| Symbol | Coin |
|---|---|
| `BITCOIN` | Bitcoin |
| `ETHEREUM` | Ethereum |
| `SOLANA` | Solana |
| `TETHER` | Tether |
| `BINANCECOIN` | BNB |
| `XRP` | XRP |
| `CARDANO` | Cardano |
| `DOGECOIN` | Dogecoin |
| `AVALANCHE-2` | Avalanche |
| `POLKADOT` | Polkadot |

---

## Database Schema

### `raw_prices`

| Column | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `symbol` | string | Coin symbol (uppercase) |
| `open` | float | Opening price |
| `high` | float | Highest price in period |
| `low` | float | Lowest price in period |
| `close` | float | Closing price |
| `timestamp` | datetime | Candle open time (UTC) |

Unique constraint on `(symbol, timestamp)` — prevents duplicate candles.

### `processed_metrics`

| Column | Type | Description |
|---|---|---|
| `id` | integer | Primary key |
| `symbol` | string | Coin symbol (uppercase) |
| `moving_avg` | float | Rolling average of close price |
| `volatility` | float | Rolling standard deviation of close price |
| `timestamp` | datetime | Corresponding candle timestamp (UTC) |

Unique constraint on `(symbol, timestamp)` — upserts on recompute.

---

## Analytics

Metrics are computed using a **rolling window of 7 candles** (configurable).

**Moving Average** — the mean closing price over the last 7 candles. Smooths out short-term noise to reveal trend direction.

**Volatility** — the standard deviation of closing prices over the last 7 candles. High volatility = large price swings. Low volatility = stable price.

Both metrics use `min_periods=1` so early rows are never empty — the window fills progressively from the first available candle.

---

## Design Decisions

**Idempotent ingestion** — the pipeline can be run multiple times safely. Raw prices use `ON CONFLICT DO NOTHING` (candle data never changes). Processed metrics use `ON CONFLICT DO UPDATE` (analytics can be recomputed with new parameters).

**Separation of raw and processed data** — raw OHLC data is stored untouched in `raw_prices`. Analytics are computed separately and stored in `processed_metrics`. This allows recomputing metrics with different parameters without re-fetching from the API.

**Service layer** — database query logic lives in `app/services/` rather than directly in route handlers. This keeps routes thin and makes business logic reusable and testable.

**Cron over in-app scheduler** — a Linux cron job triggers the pipeline weekly rather than embedding a scheduler inside the API process. This is more reliable — the scheduler survives API restarts and does not couple pipeline execution to API uptime.

---

## Future Improvements

- Deploy to cloud
- Replace cron with a workflow orchestrator (e.g., Airflow)
- Add Redis caching for frequently queried endpoints
- Migrate from CoinGecko to Binance API for real-time (minute-level) candle data
- Add Kafka for event-driven ingestion at scale
- Add support for dynamically registering new coins via `POST /symbols`

# 📊 Crypto Market Data Pipeline & API

A production-style data engineering project that ingests, processes, stores, and serves cryptocurrency market data using a modern, containerized stack.

---

## 🚀 Overview

This project builds an end-to-end data pipeline that:

* Collects historical OHLC (Open, High, Low, Close) data from the CoinGecko API
* Stores raw and processed data in a PostgreSQL database
* Applies incremental loading to avoid duplicate ingestion
* Computes analytics such as moving averages and volatility
* Exposes the data through a FastAPI backend
* Runs on a scheduled basis using cron
* Is fully containerized using Docker

---

## 🧠 Architecture

```
CoinGecko API
      ↓
Ingestion Pipeline (Python)
      ↓
PostgreSQL Database
      ↓
FastAPI Backend
      ↓
Client / API Consumer
```

---

## ⚙️ Tech Stack

* **Python** (data pipeline & backend)
* **PostgreSQL** (data storage)
* **SQLAlchemy & Alembic** (ORM & migrations)
* **FastAPI** (API layer)
* **Docker & Docker Compose** (containerization)
* **cron** (scheduling)

---

## 📂 Project Structure

```
│── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── db/          # FastAPI entry point
│
pipelines/
├── ingest.py         # Data ingestion pipeline
├── metrics.py
│
alembic/              # Database migrations
│── Dockerfile
docker-compose.yml
.env
```

---

## 🔄 Data Pipeline

### 1. Ingestion

* Fetches OHLC data for selected cryptocurrencies
* Supports multiple assets (Bitcoin, Ethereum, Solana, etc.)

### 2. Transformation

* Converts raw API data into structured format
* Standardizes timestamps
* Adds asset identifiers

### 3. Incremental Loading

* Queries the latest timestamp per asset
* Inserts only new records
* Prevents duplicates using:

  * Database constraints
  * `ON CONFLICT DO NOTHING`

### 4. Storage

* Data is stored in a normalized schema:

**raw_prices**

```
symbol | timestamp | open | high | low | close
```

**processed_metrics**

```
symbol | timestamp | moving_avg | volatility
```

---

## 📡 API Endpoints

### Health Check

```
GET /
```

### Get Latest Prices

```
GET /prices/{symbol}?limit=10
```

### Get Metrics

```
GET /metrics/{symbol}
```

---

## 🐳 Running the Project (Docker)

### 1. Build and start services

```
docker compose up --build
```

### 2. Run ingestion manually

```
docker compose run --rm api python pipelines/ingest.py
```

---

## ⏱ Scheduling (Weekly Automation)

A cron job is used to trigger the ingestion pipeline:

```
0 2 * * 0 cd /path/to/project && docker compose run --rm api python pipelines/ingest.py >> cron.log 2>&1
```

* Runs every Sunday at 2 AM
* Spins up a temporary container
* Executes ingestion
* Logs output

---

## 📈 Future Improvements

* Deploy to cloud (Render, Railway, or VPS)
* Replace cron with a workflow orchestrator (e.g., Airflow)
* Add alerting and monitoring
* Implement pagination for API endpoints
* Add caching layer (Redis)
* Introduce authentication and rate limiting

---

## 💡 What This Project Demonstrates

* End-to-end data pipeline design
* Incremental data ingestion strategies
* Relational database modeling
* Backend API development
* Containerized workflows
* Production-style thinking with clean architecture

---


from fastapi import FastAPI
from app.api import prices, metrics, pipeline

app = FastAPI(
    title="Market Data Pipeline API",
    version="1.0.0",
    description="""
## Real-Time Crypto Market Data API

This API provides cleaned and structured cryptocurrency market data including
OHLC prices, computed analytics (moving averages, volatility), and trading signals.

### Supported Coins
BITCOIN, ETHEREUM, SOLANA, TETHER, BINANCECOIN, XRP, CARDANO, DOGECOIN, AVALANCHE-2, POLKADOT

### Date Format
All date parameters must be in ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`
Example: `2025-01-01T00:00:00`

### Symbol Format
All symbols must be **uppercase**. Example: `BITCOIN`, not `bitcoin`
    """,
    contact={
        "name": "Market Data Pipeline",
    }
)

app.include_router(prices.router, prefix="/prices", tags=["Prices"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

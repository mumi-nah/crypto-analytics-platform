from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.schemas.prices import RawPriceResponse, LatestPriceResponse
from app.services.prices import get_latest_price, get_price_history

router = APIRouter()

SUPPORTED_COINS = [
    "BITCOIN", "ETHEREUM", "SOLANA", "TETHER", "BINANCECOIN",
    "XRP", "CARDANO", "DOGECOIN", "AVALANCHE-2", "POLKADOT"
]

COIN_LIST_STR = ", ".join(SUPPORTED_COINS)


@router.get(
    "/latest",
    response_model=LatestPriceResponse,
    summary="Get latest price for a coin",
    description=f"""
Returns the most recent OHLC entry for a given coin.

**Supported coins:** {COIN_LIST_STR}

**Example:** `/prices/latest?symbol=BITCOIN`
    """
)
def latest_price(
    symbol: str = Query(
        ...,
        description=f"Coin symbol in uppercase. Supported values: \
          {COIN_LIST_STR}",
        examples=["BITCOIN"]
    ),
    db: Session = Depends(get_db)
):
    if symbol.upper() not in SUPPORTED_COINS:
        raise HTTPException(
            status_code=400,
            detail=f"'{symbol}' is not supported. Supported coins: \
                {COIN_LIST_STR}"
        )
    result = get_latest_price(symbol, db)
    if not result:
        raise HTTPException(status_code=404,
                            detail=f"{symbol} not found in DB")
    return result


@router.get(
    "/history/range",
    response_model=list[RawPriceResponse],
    summary="Get historical prices for a date range",
    description=f"""
Returns paginated OHLC price history for a coin within a date range.

**Supported coins:** {COIN_LIST_STR}

**Date format:** ISO 8601 — `YYYY-MM-DDTHH:MM:SS` e.g. `2025-01-01T00:00:00`

**Pagination:** Use `limit` and `offset` to page through results. Max limit is 1000.

**Example:** `/prices/history/range?symbol=BITCOIN&start=2025-01-01T00:00:00&end=2025-06-01T00:00:00`
    """
)
def price_history(
    symbol: str = Query(
        ...,
        description=f"Coin symbol in uppercase. Supported: {COIN_LIST_STR}",
        examples=["BITCOIN"]
    ),
    start: datetime = Query(
        ...,
        description="Start date in ISO 8601 format: YYYY-MM-DDTHH:MM:SS",
        examples=["2025-01-01T00:00:00"]
    ),
    end: datetime = Query(
        ...,
        description="End date in ISO 8601 format: YYYY-MM-DDTHH:MM:SS",
        examples=["2025-12-31T00:00:00"]
    ),
    limit: int = Query(100, le=1000,
                       description="Number of rows to return. Max 1000."),
    offset: int = Query(0, 
                        description="Number of rows to skip for pagination."),
    db: Session = Depends(get_db)
):
    if symbol.upper() not in SUPPORTED_COINS:
        raise HTTPException(
            status_code=400,
            detail=f"'{symbol}' is not supported. Supported coins: \
                {COIN_LIST_STR}"
        )
    results = get_price_history(symbol, start, end, limit, offset, db)
    if not results:
        raise HTTPException(status_code=404,
                            detail="No data found for this range")
    return results


@router.get(
    "/hloc",
    response_model=list[RawPriceResponse],
    summary="Get HLOC candlestick data",
    description=f"""
Returns OHLC (High, Low, Open, Close) candlestick data for a coin within a date range.

**Supported coins:** {COIN_LIST_STR}

**Date format:** ISO 8601 — `YYYY-MM-DDTHH:MM:SS` e.g. `2025-01-01T00:00:00`

**Example:** `/prices/hloc?symbol=BITCOIN&start=2025-01-01T00:00:00&end=2025-06-01T00:00:00`
    """
)
def hloc(
    symbol: str = Query(
        ...,
        description=f"Coin symbol in uppercase. Supported: {COIN_LIST_STR}",
        examples=["BITCOIN"]
    ),
    start: datetime = Query(
        ...,
        description="Start date in ISO 8601 format: YYYY-MM-DDTHH:MM:SS",
        examples=["2025-01-01T00:00:00"]
    ),
    end: datetime = Query(
        ...,
        description="End date in ISO 8601 format: YYYY-MM-DDTHH:MM:SS",
        examples=["2025-12-31T00:00:00"]
    ),
    db: Session = Depends(get_db)
):
    if symbol.upper() not in SUPPORTED_COINS:
        raise HTTPException(
            status_code=400,
            detail=f"'{symbol}' is not supported. Supported coins: \
                {COIN_LIST_STR}"
        )
    results = get_price_history(symbol, start,
                                end, limit=1000, offset=0, db=db)
    if not results:
        raise HTTPException(status_code=404, detail="No HLOC data found")
    return results

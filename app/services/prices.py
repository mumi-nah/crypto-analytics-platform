from app.models.prices import RawPrice, ProcessedMetric
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import desc


def get_latest_price(symbol: str, db: Session):
    return (
        db.query(RawPrice)
        .filter(RawPrice.symbol == symbol.upper())
        .order_by(desc(RawPrice.timestamp))
        .first()
    )


def get_price_history(
        symbol: str,
        start: datetime,
        end: datetime,
        limit: int,
        offset: int,
        db: Session
):
    return (
        db.query(RawPrice)
        .filter(
            RawPrice.symbol == symbol.upper(),
            RawPrice.timestamp >= start,
            RawPrice.timestamp <= end
        )
        .order_by(RawPrice.timestamp)
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_latest_metrics(symbol: str, db: Session):
    return (
        db.query(ProcessedMetric)
        .filter(ProcessedMetric.symbol == symbol.upper())
        .order_by(desc(ProcessedMetric.timestamp))
        .first()
    )


def get_signal(symbol: str, db: Session):
    latest_price = get_latest_price(symbol, db)
    latest_metrics = get_latest_metrics(symbol, db)

    if not latest_price or not latest_metrics:
        return None
    if latest_price.close > latest_metrics.moving_avg:
        signal = "BUY"
    elif latest_price.close < latest_metrics.moving_avg:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "symbol":  symbol.upper(),
        "signal": signal,
        "close": latest_price.close,
        "moving_avg": latest_metrics.moving_avg,
        "timestamp": latest_price.timestamp
    }

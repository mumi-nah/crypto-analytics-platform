from fastapi import APIRouter, Depends, HTTPException  # Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.prices import MetricsResponse, SignalResponse
from app.services.prices import get_latest_metrics, get_signal

router = APIRouter()


@router.get("/signals/{symbol}", response_model=SignalResponse)
def signal(symbol: str, db: Session = Depends(get_db)):
    result = get_signal(symbol, db)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"No signal data for {symbol}")
    return result


@router.get("/{symbol}", response_model=MetricsResponse)
def metrics(symbol: str, db: Session = Depends(get_db)):
    result = get_latest_metrics(symbol, db)
    if not result:
        raise HTTPException(
            status_code=404, detail=f"No metrics found for {symbol}")
    return result

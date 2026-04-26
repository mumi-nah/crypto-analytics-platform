from fastapi import APIRouter, HTTPException
from app.schemas.prices import IngestRequest, IngestResponse
from pipeline.fetch import fetch_ohlc, transform_ohlc
from pipeline.fetch import save_to_db

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def trigger_ingest(body: IngestRequest):
    coin = body.symbol.lower()

    raw_data = fetch_ohlc(coin)
    if raw_data is None:
        raise HTTPException(
            status_code=400, detail=f"{coin} could not be fetched")

    df = transform_ohlc(coin, raw_data)
    save_to_db(df)

    return {"symbol": coin, "status": "success", "rows_inserted": len(df)}

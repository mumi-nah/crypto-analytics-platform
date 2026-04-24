from pydantic import BaseModel
from datetime import datetime


class RawPriceResponse(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    timestamp: datetime

    class Config:
        from_attributes = True


class LatestPriceResponse(BaseModel):
    symbol: str
    close: float
    timestamp: datetime

    class Config:
        from_attributes = True


class MetricsResponse(BaseModel):
    symbol: str
    moving_avg: float
    volatility: float
    timestamp: datetime

    class Config:
        from_attributes = True


class SignalResponse(BaseModel):
    symbol: str
    signal: str
    close: float
    moving_avg: float
    timestamp: datetime


class IngestRequest(BaseModel):
    symbol: str


class IngestResponse(BaseModel):
    symbol: str
    status: str
    rows_inserted: int

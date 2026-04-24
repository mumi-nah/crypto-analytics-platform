from sqlalchemy import Column, Integer, Float, String, DateTime, \
      UniqueConstraint
from app.db.base import Base


class RawPrice(Base):
    __tablename__ = "raw_prices"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_s_timestamp"),
    )


class ProcessedMetric(Base):
    __tablename__ = "processed_metrics"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    moving_avg = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_sym_timestamp"),
    )

import time
import logging
import pandas as pd
from app.db.session import SessionLocal
from app.models.prices import RawPrice, ProcessedMetric
from sqlalchemy.dialects.postgresql import insert

logging.basicConfig(
    filename='metrics_marketdata.log',
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s: %(message)s'
)


def compute_metric(symbol: str) -> pd.DataFrame:
    with SessionLocal() as session:
        rows = (
            session.query(RawPrice)
            .filter(RawPrice.symbol == symbol.upper())
            .order_by(RawPrice.timestamp)
            .all()
        )

        if not rows:
            logging.warning(f"No data found for {symbol}")
            return pd.DataFrame()

        df = pd.DataFrame([{
            "symbol": r.symbol,
            "close": r.close,
            "timestamp": r.timestamp
        } for r in rows])

        df["moving_avg"] = df["close"].rolling(window=7, min_periods=1).mean()
        df["volatility"] = df["close"].rolling(window=7,
                                               min_periods=1).std().fillna(1)
        return df[['symbol', 'timestamp', 'moving_avg', 'volatility']]


def save_metrics(df: pd.DataFrame) -> None:
    with SessionLocal() as session:
        try:
            records = df.to_dict(orient="records")

            stmtt = insert(ProcessedMetric).values(records)
            stmtt = stmtt.on_conflict_do_update(
                index_elements=["symbol", "timestamp"],
                set_={
                    'moving_avg': stmtt.excluded.moving_avg,
                    'volatility': stmtt.excluded.volatility,
                    }
            )
            session.execute(stmtt)
            session.commit()
            logging.info(f'Inserted {len(records)} rows into DB')
        except Exception as e:
            session.rollback()
            logging.error(f'Metrics compute failed for {df["symbol"][0]}: {e}')


def run_metrics(symbol: str, force_refresh: bool = False) -> None:
    """
    run the pipeline to fetch the data and save to db
    """
    try:
        df = compute_metric(symbol)
        if df.empty:
            logging.warning(f"No metrics computed for {symbol}")
            return
        save_metrics(df)
        logging.info(f'Inserted {len(df)} rows into DB')
    except Exception as e:
        logging.error(f"Pipeline failed for {symbol}: {e}")
        return None


if __name__ == "__main__":
    coins = ['bitcoin', 'ethereum', 'solana', 'tether', 'binancecoin',
             'cardano', 'dogecoin', 'avalanche-2', 'polkadot']
    for coin in coins:
        run_metrics(coin)
        time.sleep(2)

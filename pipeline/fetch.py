
import os
import time
import logging
import requests
import pandas as pd
from pandas import DataFrame
from app.models.prices import RawPrice
from app.db.session import SessionLocal
from sqlalchemy.dialects.postgresql import insert


logging.basicConfig(
    filename='fetch_marketdata.log',
    level=logging.INFO,
    format='%(asctime)s: %(levelname)s: %(message)s'
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

base_url = os.getenv('BASE_URL')


def fetch_ohlc(coin: str) -> list | None:
    """
    Fetch 365 days of OHLC data for a single coin.

    param:
        coin id to fetch. e.g "bitcoin"
    Returns:
        list of OHLC data or None if failed
    """
    url = base_url.format(coin=coin)

    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            logging.error(f'{coin} Failed with Status {response.status_code}')
            return None

        data = response.json()
        logging.info(f'{coin}: fetched {len(data)} candles')
        return data

    except requests.exceptions.RequestException as e:
        logging.exception(f'{coin}: {e}')
        return None


def transform_ohlc(coin: str, raw_data: list) -> pd.DataFrame:
    """
    Convert raw OHLC list into a structured DataFrame.
    """
    df = pd.DataFrame(
        raw_data,
        columns=['timestamp', 'open', 'high', 'low', 'close']
    )
    df['symbol'] = coin.upper()
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    logging.info('Transformation complete')

    return df


def save_to_db(df: pd.DataFrame) -> None:
    with SessionLocal() as session:
        try:
            records = df.to_dict(orient='records')

            stmtt = insert(RawPrice).values(records)
            stmtt = stmtt.on_conflict_do_nothing(
                index_elements=['symbol', 'timestamp']
            )
            session.execute(stmtt)
            session.commit()
            logging.info(f'Inserted {len(records)} rows into DB)')
            return len(records)

        except Exception as e:
            session.rollback()
            logging.error(f'DB insert failed: {e}')
            return 0


def already_ingested(coin: str) -> bool:
    """
    Check if data for this coin already exists in the DB.
    """
    session = SessionLocal()

    try:
        exists = session.query(RawPrice).filter(
            RawPrice.symbol == coin.upper()
            ).first()
        return exists is not None
    finally:
        session.close()


def run_pipeline(coin: str, force_refresh: bool = False) -> DataFrame | None:
    """
    Control pipeline flow:
    - Load from file if exists (unless force_refresh)
    - Otherwise fetch → transform → save
    """
    try:
        if not force_refresh and already_ingested(coin):
            logging.info(f'{coin}: already in DB, skipping')
            return None

        raw_data = fetch_ohlc(coin)
        if raw_data is None:
            return None

        df = transform_ohlc(coin, raw_data)
        save_to_db(df)
    except Exception as e:
        logging.error(f'Pipeline failed for {coin}: {e}')


if __name__ == "__main__":
    coins = ['bitcoin', 'ethereum', 'solana', 'tether', 'binancecoin',
             'cardano', 'dogecoin', 'avalanche-2', 'polkadot']
    for coin in coins:
        run_pipeline(coin)
        time.sleep(2)

# python -m services.dividends.dividends_db
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from models.db_model import SessionLocal, DividendsCache
from services.dividends.dividends import get_extended_dividend_data_by_ticker


class DividendsDBManager(BaseModel):
    """
    This class manages storing and updating the dividends data cache.

    It checks whether the dividends data (fetched via get_dividend_data()) is stored.
    If stored data is older than one day, it fetches and updates the cache.
    """

    cache_duration: timedelta = timedelta(days=1)

    def get_session(self):
        return SessionLocal()

    def get_cache(self, ticker: str) -> dict | None:
        session = self.get_session()
        try:
            cache = session.query(DividendsCache).filter(DividendsCache.ticker == ticker).first()
            # сheck if found and not older than cache_duration
            if cache and (datetime.now() - cache.timestamp) < self.cache_duration:
                return json.loads(cache.data)
            return None
        finally:
            session.close()

    def save_cache(self, ticker: str, data: dict) -> None:
        session = self.get_session()
        try:
            cache = DividendsCache(
                ticker=ticker, data=json.dumps(data, default=str), timestamp=datetime.now()  # default=str converts datetime to string
            )
            session.merge(cache)
            session.commit()
        finally:
            session.close()

    def update_cache(self, ticker: str) -> dict:
        """
        Returns dividends data for the given ticker.
        If a valid cache exists (less than 1 day), it returns it.
        Otherwise, it fetches new data via get_dividend_data(), saves it, then returns it.
        """
        self.clear_outdated_cache()

        cached_data = self.get_cache(ticker)
        if cached_data is not None:
            return cached_data

        new_data = get_extended_dividend_data_by_ticker(ticker=ticker)
        self.save_cache(ticker, new_data)
        return new_data

    def clear_outdated_cache(self) -> None:
        session = self.get_session()
        try:
            outdated_time = datetime.now() - self.cache_duration
            session.query(DividendsCache).filter(DividendsCache.timestamp < outdated_time).delete()
            session.commit()
        finally:
            session.close()


# db = DividendsDBManager()
# print(db.update_cache("OZON"))

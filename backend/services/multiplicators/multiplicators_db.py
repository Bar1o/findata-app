from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from models.db_model import SessionLocal, MultiplicatorsCache
from services.multiplicators.multiplicators import get_multiplicator_data_from_api
from ..paper_data.total_tickers import missing_tickers, api_tickers
from .parse_multipl import parse_financial_data


class MultiplicatorsDBManager(BaseModel):
    """
    This class manages storing and updating the multiplicator data cache.

    It checks whether multiplicator data (fetched via get_multiplicator_data_from_api)
    is stored. If the stored data is older than cache_duration, it fetches and updates the cache.

    Updates data based on type of ticker:
    - uses parse_financial_data() if ticker in missing_tickers
    - uses api call if ticker in api_tickers
    """

    cache_duration: timedelta = timedelta(days=1)

    def get_session(self):
        return SessionLocal()

    def get_cache(self, ticker: str) -> dict | None:
        session = self.get_session()
        try:
            cache = session.query(MultiplicatorsCache).filter(MultiplicatorsCache.ticker == ticker).first()
            if cache and (datetime.now() - cache.timestamp) < self.cache_duration:
                return json.loads(cache.data)
            return None
        finally:
            session.close()

    def save_cache(self, ticker: str, data: dict) -> None:
        session = self.get_session()
        try:
            cache = MultiplicatorsCache(ticker=ticker, data=json.dumps(data, default=str), timestamp=datetime.now())
            session.merge(cache)
            session.commit()
        finally:
            session.close()

    def update_cache(self, ticker: str) -> dict:
        """
        Returns multiplicator data for the given ticker.
        If a valid cache exists (younger than cache_duration), it is returned.
        Otherwise, new data is fetched either via parsing (for missing_tickers)
        or via the external API (for api_tickers), saved, then returned.
        """
        self.clear_outdated_cache()

        cached_data = self.get_cache(ticker)
        if cached_data is not None:
            return cached_data

        if ticker in missing_tickers:
            new_data = parse_financial_data(ticker)
        elif ticker in api_tickers:
            all_data = get_multiplicator_data_from_api()
            new_data = all_data.get(ticker, {})

        self.save_cache(ticker, new_data)
        return new_data

    def clear_outdated_cache(self) -> None:
        session = self.get_session()
        try:
            outdated_time = datetime.now() - self.cache_duration
            session.query(MultiplicatorsCache).filter(MultiplicatorsCache.timestamp < outdated_time).delete()
            session.commit()
        finally:
            session.close()

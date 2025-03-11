import os
import pathlib
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import logging

from models.db_model import SessionLocal, PaperDataCache
from .paper_data import PaperData
from .ticker_table_db import TickerTableDBManager


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PaperDataDBManager(BaseModel):
    """
    This class manages storing and updating the cache for PaperData().get_main_data_on_share_by_uid() func.
    It handles only the main data (returns by ticker).
    """

    cache_duration: timedelta = timedelta(days=90)  # 3 months

    def get_session(self):
        return SessionLocal()

    def get_cache(self, ticker: str) -> dict | None:
        session = self.get_session()
        try:
            cache = session.query(PaperDataCache).filter(PaperDataCache.ticker == ticker).first()
            if cache:
                if datetime.now() - cache.timestamp < self.cache_duration:
                    return json.loads(cache.data)
            return None
        finally:
            session.close()

    def save_cache(self, ticker: str, data: dict) -> None:
        session = self.get_session()
        try:
            # use default=str to convert datetime objects to strings
            cache = PaperDataCache(ticker=ticker, data=json.dumps(data, default=str), timestamp=datetime.now())
            session.merge(cache)
            session.commit()
        finally:
            session.close()

    def update_cache(self, ticker: str) -> dict:
        """
        Updates the cache if not available or outdated.
        """
        self.clear_outdated_cache()

        cached_data = self.get_cache(ticker)
        logger.debug(f"cached_data is None:{cached_data is None}")
        if cached_data is not None:
            return cached_data

        # no valid cache exists => fetch new data
        paper_data_instance = PaperData()
        uid = TickerTableDBManager().get_uid_by_ticker(ticker)
        new_data: dict = paper_data_instance.get_main_data_on_share_by_uid(uid)
        self.save_cache(ticker, new_data)
        logger.debug(f"get new_data")
        return new_data

    def clear_outdated_cache(self) -> None:
        session = self.get_session()
        try:
            outdated_time = datetime.now() - self.cache_duration
            session.query(PaperDataCache).filter(PaperDataCache.timestamp < outdated_time).delete()
            logger.info("cleared cache")
            session.commit()
        finally:
            session.close()

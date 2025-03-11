# python -m services.paper_data.ticker_table_db
import os
import pathlib
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from models.db_model import SessionLocal, TickerTable
from .paper_data import PaperData
import pandas as pd
import logging
from .total_tickers import all_tickers

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TickerTableDBManager(BaseModel):
    """
    This class manages storing and updating the cache for get_uid_ticker_figi_data_by_ticker from PaperData.
    It handles only the uid-figi-ticker table.
    CRUD for get_uid_ticker_figi_data_by_ticker().
    DB model: TickerTable.
    Gets data from uid-figi-ticker table.

    """

    cache_duration: timedelta = timedelta(days=90)

    def get_session(self):
        return SessionLocal()

    def get_cache(self, ticker: str) -> dict | None:
        session = self.get_session()
        try:
            cache = session.query(TickerTable).filter(TickerTable.ticker == ticker).first()
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
            cache = TickerTable(ticker=ticker, data=json.dumps(data, default=str), timestamp=datetime.now())
            session.merge(cache)
            session.commit()
        finally:
            session.close()

    def update_cache(self, ticker: str) -> json:
        """
        Updates the cache if not available or outdated.
        Uses PaperData.get_uid_ticker_figi_data_by_ticker() to get fresh data.
        """
        self.clear_outdated_cache()

        cached_data = self.get_cache(ticker)
        if cached_data is not None:
            return cached_data

        paper_data_instance = PaperData()
        new_data: json = json.dumps(paper_data_instance.get_uid_ticker_figi_data_by_ticker(ticker), default=str)
        self.save_cache(ticker, new_data)
        return new_data

    def clear_outdated_cache(self) -> None:
        session = self.get_session()
        try:
            outdated_time = datetime.now() - self.cache_duration
            session.query(TickerTable).filter(TickerTable.timestamp < outdated_time).delete()
            session.commit()
        finally:
            session.close()

    ################### get data from DB #################
    def get_uid_by_ticker(self, ticker: str) -> str:
        data = self.update_cache(ticker)
        return json.loads(data)["uid"]

    def get_figi_by_ticker(self, ticker: str) -> str:
        data = self.update_cache(ticker)
        return json.loads(data)["figi"]

    def get_ticker_by_uid(self, uid: str) -> str:
        for ticker in all_tickers:
            data = json.loads(self.update_cache(ticker))
            if data["uid"] == uid:
                return ticker


db = TickerTableDBManager()
# print(db.update_cache("OZON"))
# print(db.get_uid_by_ticker("T"))
print(db.get_ticker_by_uid("T"))

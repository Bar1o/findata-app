# CRUD for db to store data from api
import json
import logging
from datetime import datetime, timedelta

from models.db_model import SessionLocal, IchimokuIndexCache
from services.ichimoku.ichimoku_api import IchimokuApi
from pydantic import BaseModel, Field, PrivateAttr


logger = logging.getLogger(__name__)


def get_cache_validity(period: str) -> timedelta:
    short_periods = ["D", "3D", "W"]
    long_periods = ["M", "3M", "Y"]
    if period in short_periods:
        return timedelta(hours=1)
    elif period in long_periods:
        return timedelta(days=1)
    else:
        return timedelta(hours=1)


class IchimokuDbManager(BaseModel):
    figi: str
    period: str

    def get_cache(self):
        session = SessionLocal()
        try:
            cache_entry = session.query(IchimokuIndexCache).filter_by(figi=self.figi, period=self.period).first()
            if cache_entry:
                time_diff = datetime.now() - cache_entry.timestamp
                validity = get_cache_validity(self.period)
                if time_diff <= validity:
                    return cache_entry
            return None
        finally:
            session.close()

    def save_cache(self, data: dict):
        session = SessionLocal()
        try:
            json_data = json.dumps(data)
            cache_entry = IchimokuIndexCache(figi=self.figi, period=self.period, data=json_data, timestamp=datetime.now())
            session.merge(cache_entry)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
        finally:
            session.close()

    def update_cache(self):
        # Uses the API class to fetch and recalc data and saves it into the db
        api_client = IchimokuApi(figi=self.figi, period=self.period)
        df = api_client.get_all_candles_by_period()
        data = api_client.export_nan(df)
        self.save_cache(data)
        logger.info("Cache updated.")

    def clear_outdated_cache(self):
        # Deletes all cache entries that are older than the allowed cache validity
        session = SessionLocal()
        try:
            validity = get_cache_validity(self.period)
            threshold = datetime.now() - validity
            rows_deleted = session.query(IchimokuIndexCache).filter(IchimokuIndexCache.timestamp < threshold).delete()
            session.commit()
            logger.info(f"Cleared {rows_deleted} outdated cache entries.")
        except Exception as e:
            logger.error(f"Error clearing outdated cache: {e}")
            session.rollback()
        finally:
            session.close()

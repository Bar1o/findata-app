from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from models.db_model import SessionLocal, PaperDataCache, AssetsTable
from .paper_data import PaperData
import pandas as pd


class PaperDataDBManager(BaseModel):
    """
    This class manages storing and updating the cache for PaperData.
    It handles both the main data (by ticker) and the assets table.
    It:
    - Checks if the asset table (from get_assets_table()) has been saved.
    - Loads stored data into PaperData.main_data.
    - Uses export_main_data_json_by_ticker() to generate JSON data.
    - Updates the stored cache if the record is older than 3 months.
    - Clears outdated records.
    """

    cache_duration: timedelta = timedelta(days=90)  # 3 months

    def get_session(self):
        return SessionLocal()

    def get_cache(self, ticker: str) -> dict | None:
        session = self.get_session()
        try:
            cache = session.query(PaperDataCache).filter(PaperDataCache.ticker == ticker).first()
            if cache:
                # Check if cache is not older than 3 months.
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
        Uses PaperData.export_main_data_json_by_ticker() to get fresh data.
        """
        self.clear_outdated_cache()

        cached_data = self.get_cache(ticker)
        if cached_data is not None:
            return cached_data

        # no valid cache exists => fetch new data.
        paper_data_instance = PaperData()
        new_data = paper_data_instance.export_main_data_json_by_ticker(ticker)
        self.save_cache(ticker, new_data)
        return new_data

    def clear_outdated_cache(self) -> None:
        session = self.get_session()
        try:
            outdated_time = datetime.now() - self.cache_duration
            session.query(PaperDataCache).filter(PaperDataCache.timestamp < outdated_time).delete()
            session.commit()
        finally:
            session.close()

    def check_assets_table(self) -> list[dict]:
        """
        Checks if the asset table (from PaperData.get_assets_table()) is stored in the DB.
        If not, fetches the asset data, saves each row into the AssetsTable and returns the data.
        Returns a list of dicts with columns ['uid', 'name', 'figi', 'ticker', 'class_code'].
        """
        session = self.get_session()
        try:
            stored_assets = session.query(AssetsTable).all()
            if stored_assets:
                return [
                    {
                        "uid": asset.uid,
                        "name": asset.name,
                        "figi": asset.figi,
                        "ticker": asset.ticker,
                        "class_code": asset.class_code,
                    }
                    for asset in stored_assets
                ]
            else:
                # No assets in the DB; fetch via PaperData.
                paper_data_instance = PaperData()
                assets_df: pd.DataFrame = paper_data_instance.get_assets_table()
                # Insert each asset row into the AssetsTable.
                for _, row in assets_df.iterrows():
                    asset = AssetsTable(
                        uid=row["uid"],
                        name=row["name"],
                        figi=row["figi"],
                        ticker=row["ticker"],
                        class_code=row["class_code"],
                    )
                    session.add(asset)
                session.commit()
                return assets_df.to_dict(orient="records")
        finally:
            session.close()

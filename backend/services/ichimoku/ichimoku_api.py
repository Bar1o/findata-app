import os
import json
import pandas as pd
from datetime import timedelta
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from dotenv import load_dotenv
import logging
from pandas import DataFrame
from pydantic import BaseModel, Field, PrivateAttr

from ..paper_data.paper_data_db import PaperDataDBManager
from models.models import Quotation, factor, Window, Candle, convert_quotation

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
load_dotenv()

db_manager = PaperDataDBManager()

TOKEN = os.environ["INVEST_TOKEN"]

timedelta_type = {
    "D": timedelta(days=1),
    "3D": timedelta(days=3),
    "W": timedelta(days=7),
    "M": timedelta(days=30),
    "3M": timedelta(days=90),
    "Y": timedelta(weeks=52),
}

interval_type = {
    "D": CandleInterval.CANDLE_INTERVAL_HOUR,
    "3D": CandleInterval.CANDLE_INTERVAL_HOUR,
    "W": CandleInterval.CANDLE_INTERVAL_HOUR,
    "M": CandleInterval.CANDLE_INTERVAL_4_HOUR,
    "3M": CandleInterval.CANDLE_INTERVAL_DAY,
    "Y": CandleInterval.CANDLE_INTERVAL_DAY,
}


class IchimokuApi(BaseModel):
    ticker: str
    period: str

    _all_candles: list = []

    def make_candle(self, candle) -> dict:
        return {
            "time": candle.time,
            "open": convert_quotation(candle.open),
            "close": convert_quotation(candle.close),
            "high": convert_quotation(candle.high),
            "low": convert_quotation(candle.low),
            "volume": candle.volume,
        }

    def normalize_candles(self, all_candles: list) -> DataFrame:
        return DataFrame(all_candles)

    def get_ichimoku(self, df: DataFrame, wi: Window = Window(small=9, medium=26, large=52)) -> DataFrame:
        df["tenkanSen"] = (df["high"].rolling(window=wi.small).max() + df["low"].rolling(window=wi.small).min()) / 2
        df["kijunSen"] = (df["high"].rolling(window=wi.medium).max() + df["low"].rolling(window=wi.medium).min()) / 2
        df["senkouSpanA"] = ((df["tenkanSen"] + df["kijunSen"]) / 2).shift(wi.medium)
        df["senkouSpanB"] = ((df["high"].rolling(window=wi.large).max() + df["low"].rolling(window=wi.large).min()) / 2).shift(wi.medium)
        df["chikouSpan"] = df["close"].shift(-wi.medium)
        return df

    def get_all_candles_by_period(self) -> DataFrame:
        figi = db_manager.get_figi_by_ticker(self.ticker)
        try:
            self._all_candles.clear()
            with Client(TOKEN) as client:
                for candle in client.get_all_candles(
                    figi=figi,
                    from_=now() - timedelta_type[self.period],
                    interval=interval_type[self.period],
                ):
                    self._all_candles.append(self.make_candle(candle))
            df = self.normalize_candles(self._all_candles)
            df = self.get_ichimoku(df)
            logger.info("get_all_candles_by_period: exported the data")
            return df
        except Exception as e:
            logger.error(f"Error fetching API data: {e}")
            raise

    def export_nan(self, df: DataFrame) -> list:
        result = []
        for _, row in df.iterrows():
            unix_time = int(row["time"].timestamp())
            if row.isna().all():
                result.append({"time": unix_time})
            else:
                data_dict = {"time": unix_time}
                for col in df.columns:
                    if col != "time" and not pd.isna(row[col]):
                        data_dict[col] = row[col]
                result.append(data_dict)
        return result

    def get_exported_data(self) -> dict:
        df = self.get_all_candles_by_period()
        json_data = self.export_nan(df)
        logger.info("get_exported_data: data exported successfully")
        return {"data": json_data}


IchimokuApi(ticker="SBER", period="W").get_exported_data()

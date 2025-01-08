import os
import json
from datetime import timedelta, datetime
from fastapi import HTTPException
from pandas import DataFrame
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from dotenv import load_dotenv
import pandas as pd
import logging
from pydantic import BaseModel, Field, PrivateAttr
from typing import Dict, List, Literal

from models.models import Quotation, factor, Window, Candle


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.environ["INVEST_TOKEN"]


timedelta_type: Dict[str, datetime] = {
    "D": timedelta(days=1),
    "3D": timedelta(days=3),
    "W": timedelta(days=7),
    "M": timedelta(days=30),
    "3M": timedelta(days=90),
    "Y": timedelta(weeks=52),
}
interval_type: Dict[str, datetime] = {
    "D": CandleInterval.CANDLE_INTERVAL_HOUR,
    "3D": CandleInterval.CANDLE_INTERVAL_HOUR,
    "W": CandleInterval.CANDLE_INTERVAL_HOUR,
    "M": CandleInterval.CANDLE_INTERVAL_4_HOUR,
    "3M": CandleInterval.CANDLE_INTERVAL_DAY,
    "Y": CandleInterval.CANDLE_INTERVAL_DAY,
}


class IchimokuIndex(BaseModel):
    figi: str
    period: str

    _df: DataFrame = PrivateAttr()
    _all_candles: list = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._all_candles = []
        self._df = self.get_all_candles_by_period()  # <- main method

    @staticmethod
    def convert_quotation(q: Quotation):
        return q.units + q.nano / factor

    def make_candle(self, candle) -> dict:
        return {
            "time": candle.time,
            "open": self.convert_quotation(candle.open),
            "close": self.convert_quotation(candle.close),
            "high": self.convert_quotation(candle.high),
            "low": self.convert_quotation(candle.low),
            "volume": candle.volume,
        }

    def normalize_candles(self, all_candles: list) -> DataFrame:
        df = DataFrame(all_candles)
        return df

    def get_ichimoku(self, df: DataFrame, wi: Window = Window(small=9, medium=26, large=52)) -> DataFrame:
        df["tenkanSen"] = (df["high"].rolling(window=wi.small).max() + df["low"].rolling(window=wi.small).min()) / 2
        df["kijunSen"] = (df["high"].rolling(window=wi.medium).max() + df["low"].rolling(window=wi.medium).min()) / 2
        df["senkouSpanA"] = ((df["tenkanSen"] + df["kijunSen"]) / 2).shift(wi.medium)
        df["senkouSpanB"] = ((df["high"].rolling(window=wi.large).max() + df["low"].rolling(window=wi.large).min()) / 2).shift(wi.medium)
        df["chikouSpan"] = df["close"].shift(-wi.medium)
        return df

    def export_nan(self, df: DataFrame) -> DataFrame:

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

    def get_all_candles_by_period(self) -> list:
        try:
            self._all_candles.clear()

            with Client(TOKEN) as client:
                for candle in client.get_all_candles(
                    figi=self.figi,
                    from_=now() - timedelta_type[self.period],
                    interval=interval_type[self.period],
                ):
                    self._all_candles.append(self.make_candle(candle))
            df = self.normalize_candles(self._all_candles)
            df = self.get_ichimoku(df)
            logger.info("get_all_candles_by_period: exported the data")

            return df
        except Exception as e:
            logger.error(f"Error: {e}")
            raise HTTPException(status_code=500, detail="get_all_candles_by_period error")

    def get_exported_data(self) -> dict:
        json_data = self.export_nan(self._df)
        return {"data": json_data}


print(IchimokuIndex(figi="BBG004730N88", period="W").get_exported_data())

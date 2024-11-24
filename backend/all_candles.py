import os
import json
from datetime import timedelta
from fastapi import HTTPException
from pandas import DataFrame
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from dotenv import load_dotenv
from modules.modules import Quotation, factor, Window, Candle
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.environ["INVEST_TOKEN"]

all_candles = []


def convert_quotation(q: Quotation):
    return q.units + q.nano / factor


def make_candle(candle) -> dict:
    return {
        "time": candle.time,
        "open": convert_quotation(candle.open),
        "close": convert_quotation(candle.close),
        "high": convert_quotation(candle.high),
        "low": convert_quotation(candle.low),
        "volume": candle.volume,
    }


def normalize_candles(all_candles: list) -> DataFrame:
    df = DataFrame(all_candles)
    return df


def get_ichimoku(df: DataFrame, wi: Window = Window(small=9, medium=26, large=52)) -> DataFrame:
    df["tenkanSen"] = (df["high"].rolling(window=wi.small).max() + df["low"].rolling(window=wi.small).min()) / 2
    df["kijunSen"] = (df["high"].rolling(window=wi.medium).max() + df["low"].rolling(window=wi.medium).min()) / 2
    df["senkouSpanA"] = ((df["tenkanSen"] + df["kijunSen"]) / 2).shift(wi.medium)
    df["senkouSpanB"] = ((df["high"].rolling(window=wi.large).max() + df["low"].rolling(window=wi.large).min()) / 2).shift(wi.medium)
    df["chikouSpan"] = df["close"].shift(-wi.medium)
    return df


def export(df: DataFrame) -> list:
    df["time"] = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df.to_dict(orient="records")


def get_all_candles_by_figi(figi: str) -> list:
    all_candles.clear()
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(days=90 * 4),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            all_candles.append(make_candle(candle))
    df = normalize_candles(all_candles)
    df = get_ichimoku(df)

    return export(df)


def get_all_candles_by_period(figi: str, period: str) -> list:
    try:
        all_candles.clear()
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
            "M": CandleInterval.CANDLE_INTERVAL_DAY,
            "3M": CandleInterval.CANDLE_INTERVAL_DAY,
            "Y": CandleInterval.CANDLE_INTERVAL_DAY,
        }
        with Client(TOKEN) as client:
            for candle in client.get_all_candles(
                figi=figi,
                from_=now() - timedelta_type[period],
                interval=interval_type[period],
            ):
                all_candles.append(make_candle(candle))
        df = normalize_candles(all_candles)
        df = get_ichimoku(df)
        logger.info("get_all_candles_by_period: exported the data")

        return export(df)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="get_all_candles_by_period error")


print(get_all_candles_by_period("BBG004730N88", "D"))

# if __name__ == "__main__":
#     main()

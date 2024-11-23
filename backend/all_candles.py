import os
import json
from datetime import timedelta
from pandas import DataFrame
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from dotenv import load_dotenv
from modules.modules import Quotation, factor, Window, Candle
import pandas as pd

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
    df["tenkan-sen"] = (df["high"].rolling(window=wi.small).max() + df["low"].rolling(window=wi.small).min()) / 2
    df["kijun-sen"] = (df["high"].rolling(window=wi.medium).max() + df["low"].rolling(window=wi.medium).min()) / 2
    df["senkou span A"] = ((df["tenkan-sen"] + df["kijun-sen"]) / 2).shift(wi.medium)
    df["senkou span B"] = ((df["high"].rolling(window=wi.large).max() + df["low"].rolling(window=wi.large).min()) / 2).shift(wi.medium)
    df["chikou span"] = df["close"].shift(-wi.medium)
    return df


def export(df: DataFrame) -> list:
    df["time"] = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df.to_dict(orient="records")


def get_all_candles_by_figi(figi: str) -> list:
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(days=3),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
        ):
            all_candles.append(make_candle(candle))
    df = normalize_candles(all_candles)
    df = get_ichimoku(df)

    return export(df)


print(get_all_candles_by_figi("BBG004730N88"))

# if __name__ == "__main__":
#     main()

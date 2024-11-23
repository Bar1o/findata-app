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
        "Time": candle.time,
        "Open": convert_quotation(candle.open),
        "Close": convert_quotation(candle.close),
        "Max": convert_quotation(candle.high),
        "Min": convert_quotation(candle.low),
        "Volume": candle.volume,
    }


def normalize_candles(all_candles: list) -> DataFrame:
    df = DataFrame(all_candles)
    return df


def get_ichimoku(df: DataFrame, wi: Window = Window(small=9, medium=26, large=52)) -> DataFrame:
    df["Tenkan-sen"] = (df["Max"].rolling(window=wi.small).max() + df["Min"].rolling(window=wi.small).min()) / 2
    df["Kijun-sen"] = (df["Max"].rolling(window=wi.medium).max() + df["Min"].rolling(window=wi.medium).min()) / 2
    df["Senkou Span A"] = ((df["Tenkan-sen"] + df["Kijun-sen"]) / 2).shift(wi.medium)
    df["Senkou Span B"] = ((df["Max"].rolling(window=wi.large).max() + df["Min"].rolling(window=wi.large).min()) / 2).shift(wi.medium)
    df["Chikou Span"] = df["Close"].shift(-wi.medium)
    return df


def export(df: DataFrame) -> list:
    df["Time"] = df["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df.to_dict(orient="records")


def get_all_candles_by_figi(figi: str) -> list:
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
            figi=figi,
            from_=now() - timedelta(days=5),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
        ):
            all_candles.append(make_candle(candle))
    df = normalize_candles(all_candles)
    df = get_ichimoku(df)

    return export(df)


print(get_all_candles_by_figi("BBG004730N88"))

# if __name__ == "__main__":
#     main()

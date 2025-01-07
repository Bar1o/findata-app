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


# def fill_with_empty_data(all_candles: DataFrame) -> DataFrame:
#     all_candles["time"] = pd.to_datetime(all_candles["time"])
#     all_candles.set_index("time", inplace=True)

#     # Create a complete hourly time range
#     full_range = pd.date_range(start=all_candles.index.min(), end=all_candles.index.max(), freq="h")
#     all_candles = all_candles.reindex(full_range)

#     # Identify hours from 20:00 to 4:00 and set them to NaN
#     mask = (all_candles.index.hour >= 21) | (all_candles.index.hour < 4)
#     all_candles.loc[mask] = pd.NA

#     all_candles.reset_index(inplace=True)
#     all_candles.rename(columns={"index": "time"}, inplace=True)

#     return all_candles


def export(df: DataFrame) -> list:
    df["time"] = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    # return df.to_dict(orient="records")
    # df.set_index("time", inplace=True)
    return df.to_dict(orient="records")


# def calc_buy_sell_signals(df: DataFrame):
#     buySignals = (df["tenkanSen"] > df["kijunSen"]) & (df["tenkanSen"].shift(1) <= df["kijunSen"].shift(1))
#     sellSignals = (df["tenkanSen"] < df["kijunSen"]) & (df["tenkanSen"].shift(1) >= df["kijunSen"].shift(1))

#     bS = df["low"][buySignals].to_json()
#     sS = df["high"][sellSignals].to_json()
#     return bS, sS


def export_nan(df: DataFrame) -> list:

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


# def calc_buy_sell_signals(df: DataFrame) -> tuple[list]:
#     buySignals = (df["tenkanSen"] > df["kijunSen"]) & (df["tenkanSen"].shift(1) <= df["kijunSen"].shift(1))
#     sellSignals = (df["tenkanSen"] < df["kijunSen"]) & (df["tenkanSen"].shift(1) >= df["kijunSen"].shift(1))

#     # series -> df -> drop index + add value -> export as list
#     bS = df.loc[buySignals, ["time", "low"]].copy()
#     bS.rename(columns={"low": "value"}, inplace=True)
#     bS["time"] = pd.to_datetime(bS["time"])
#     bS = export_nan(bS)

#     sS = df.loc[sellSignals, ["time", "high"]].copy()
#     sS.rename(columns={"high": "value"}, inplace=True)
#     sS["time"] = pd.to_datetime(sS["time"])
#     sS = export_nan(sS)

#     return bS, sS


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
            "M": CandleInterval.CANDLE_INTERVAL_4_HOUR,
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

        json_data = export_nan(df)
        main_json_data = {"data": json_data}
        return main_json_data
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="get_all_candles_by_period error")


print(get_all_candles_by_period("BBG004730N88", "W"))

# if __name__ == "__main__":
#     main()

# python -m services.dividends.dividends
import os
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from tinkoff.invest import Client
from tinkoff.invest.schemas import GetDividendsRequest
import json
from dotenv import load_dotenv

from models.models import Quotation, convert_quotation
from ..paper_data.ticker_table_db import TickerTableDBManager
from ..multiplicators.multiplicators import Multiplicators

load_dotenv()
TOKEN = os.environ["INVEST_TOKEN"]

db_manager = TickerTableDBManager()


def get_dividend_data_by_ticker(ticker: str) -> dict:
    """Get dividend data for 1 year from today"""
    dividend_data = []
    with Client(TOKEN) as client:
        result = {}
        from_date = datetime.strptime((datetime.now() - timedelta(days=365)).strftime("%d-%m-%Y"), "%d-%m-%Y")
        to_date = datetime.strptime(datetime.now().strftime("%d-%m-%Y"), "%d-%m-%Y")

        figi = db_manager.get_figi_by_ticker(ticker)
        dividends = client.instruments.get_dividends(figi=figi, from_=from_date, to=to_date)
        for div in dividends.dividends:

            result = {
                "dividend_net": convert_quotation(Quotation(units=div.dividend_net.units, nano=div.dividend_net.nano)),
                "payment_date": div.payment_date,
                "declared_date": div.declared_date,
                "last_buy_date": div.last_buy_date,
                "dividend_type": div.dividend_type,
                "record_date": div.record_date,
                "regularity": div.regularity,
                "close_price": convert_quotation(Quotation(units=div.close_price.units, nano=div.close_price.nano)),
                "yield_value": convert_quotation(Quotation(units=div.yield_value.units, nano=div.yield_value.nano)),
                "created_at": div.created_at,
            }
        dividend_data.append(result)

    return dividend_data[0]


def get_extended_dividend_data_by_ticker(ticker: str) -> dict:
    """
    приводит get_dividend_data_by_ticker() к формату
    {
    "dividend_yield_daily_ttm": {
        "value": "10.49",
        "unit": "%"
        },
    "payment_date": {
        "value": "2024-07-21 00:00:00+00:00",
        "unit": ""
        },
    }
    """
    div_data: dict = get_dividend_data_by_ticker(ticker)
    multip_data: dict = Multiplicators().get_divs_from_multiplicator_data_from_api(ticker)

    formatted_divs = dict()
    if div_data:
        field_units = {
            "dividend_net": ("руб", 1),
            "yield_value": ("%", 1),
            "close_price": ("руб", 1),
            "payment_date": ("", 1),
            "declared_date": ("", 1),
            "last_buy_date": ("", 1),
            "record_date": ("", 1),
            "dividend_type": ("", 1),
            "regularity": ("", 1),
            "created_at": ("", 1),
        }
        for field, value in div_data.items():
            if field in field_units:
                unit, divisor = field_units[field]

                if field in ["dividend_net", "yield_value", "close_price"]:
                    formatted_value = f"{float(value):.2f}"
                else:
                    formatted_value = str(value)

                formatted_divs[field] = {
                    "value": formatted_value,
                    "unit": unit,
                }

    # объединение данные, если мультипликаторы не пустые
    if multip_data and isinstance(multip_data, dict):
        # объединение словарей с приоритетом данных из API (если они есть)
        for key, value in multip_data.items():
            if key not in formatted_divs:
                formatted_divs[key] = value

    return formatted_divs


# print(get_dividend_data_by_ticker("SVCB"))
# print(json.dumps(get_extended_dividend_data_by_ticker("SBER"), default=str, indent=2, ensure_ascii=False))

# dividend_data = get_dividend_data_by_ticker("T")
# print(json.dumps(dividend_data, default=str, indent=2))

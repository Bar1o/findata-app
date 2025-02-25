import os
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from tinkoff.invest import Client
from tinkoff.invest.schemas import GetDividendsRequest
import json
from dotenv import load_dotenv

from models.models import Quotation, convert_quotation

load_dotenv()
TOKEN = os.environ["INVEST_TOKEN"]


def get_dividend_data_by_figi(figi: str) -> dict:
    """Get dividend data for 1 year from today"""
    dividend_data = []
    with Client(TOKEN) as client:
        from_date = datetime.strptime((datetime.now() - timedelta(days=365)).strftime("%d-%m-%Y"), "%d-%m-%Y")
        to_date = datetime.strptime(datetime.now().strftime("%d-%m-%Y"), "%d-%m-%Y")

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


# dividend_data = get_dividend_data_by_figi("TCS00A107T19")
# print(json.dumps(dividend_data, default=str))

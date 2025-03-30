from tinkoff.invest import Client, Quotation
from tinkoff.invest.utils import quotation_to_decimal
from dotenv import load_dotenv
import os

from services.paper_data.ticker_table_db import TickerTableDBManager


load_dotenv()
TOKEN = os.environ["INVEST_TOKEN"]
db_manager = TickerTableDBManager()  # ticker-figi-uid table


def get_realtime_quote(ticker: str) -> dict:
    """
    Получает текущие котировки акции и рассчитывает изменения.

    Args:
        figi (str): FIGI акции (например, 'BBG004730N88')
        token (str): API-токен Tinkoff Invest

    Returns:
        dict: {
            'price': текущая цена,
            'abs_change': изменение в рублях,
            'percent_change': изменение в процентах
        }
    """

    figi: str = db_manager.get_figi_by_ticker(ticker)
    if not figi:
        return {}

    # кеширование предыдущей цены в атрибуте функции
    if not hasattr(get_realtime_quote, "prev_price"):
        get_realtime_quote.prev_price = None

    with Client(TOKEN) as client:
        response = client.market_data.get_last_prices(figi=[figi])
        current_price = float(quotation_to_decimal(response.last_prices[0].price))

    abs_change = 0.0
    percent_change = 0.0

    if get_realtime_quote.prev_price is not None:
        abs_change = current_price - get_realtime_quote.prev_price
        percent_change = (abs_change / get_realtime_quote.prev_price) * 100

    get_realtime_quote.prev_price = current_price

    return {"price": round(current_price, 2), "abs_change": round(abs_change, 2), "percent_change": round(percent_change, 2)}

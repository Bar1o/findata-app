import os
import json
from tinkoff.invest import Client
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ["INVEST_TOKEN"]

data = []


# def export_to_json(data, filename):
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)


# def main():
#     with Client(TOKEN) as client:
#         r = client.instruments.options()
#         for instrument in r.instruments:
#             data.append(instrument)
#             # print(instrument)
#     # export_to_json(json_data, "output.json")
#     print(data.size(), data[0])


# if __name__ == "__main__":
#     main()


# from tinkoff.invest.schemas import IndicativesRequest


# def main():
#     with Client(TOKEN) as client:
#         request = IndicativesRequest()
#         indicatives = client.instruments.indicatives(request=request)
#         for instrument in indicatives.instruments:
#             print(instrument.name)


# if __name__ == "__main__":
#     main()


"""Example - How to get figi by name of ticker."""
import logging
import os

from pandas import DataFrame

from tinkoff.invest import Client, SecurityTradingStatus
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.utils import quotation_to_decimal

TOKEN = os.environ["INVEST_TOKEN"]

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    """Example - How to get figi by name of ticker."""

    ticker = "EUR/USD"  # "BRH3" "SBER" "VTBR" "YDEX"

    with Client(TOKEN) as client:
        instruments: InstrumentsService = client.instruments
        tickers = []
        for method in ["shares", "bonds", "etfs", "currencies", "futures"]:
            for item in getattr(instruments, method)().instruments:
                tickers.append(
                    {
                        "name": item.name,
                        "ticker": item.ticker,
                        "class_code": item.class_code,
                        "figi": item.figi,
                        "uid": item.uid,
                        "type": method,
                        "min_price_increment": quotation_to_decimal(item.min_price_increment),
                        "scale": 9 - len(str(item.min_price_increment.nano)) + 1,
                        "lot": item.lot,
                        "trading_status": str(SecurityTradingStatus(item.trading_status).name),
                        "api_trade_available_flag": item.api_trade_available_flag,
                        "currency": item.currency,
                        "exchange": item.exchange,
                        "buy_available_flag": item.buy_available_flag,
                        "sell_available_flag": item.sell_available_flag,
                        "short_enabled_flag": item.short_enabled_flag,
                        "klong": quotation_to_decimal(item.klong),
                        "kshort": quotation_to_decimal(item.kshort),
                    }
                )

        tickers_df = DataFrame(tickers)

        ticker_df = tickers_df[tickers_df["ticker"] == ticker]
        if ticker_df.empty:
            logger.error("There is no such ticker: %s", ticker)
            return

        figi = ticker_df["figi"].iloc[0]
        print(f"\nTicker {ticker} have figi={figi}\n")
        print(f"Additional info for this {ticker} ticker:")
        print(ticker_df.iloc[0])


if __name__ == "__main__":
    main()

# import asyncio
# import os

# from tinkoff.invest import AsyncClient
# from tinkoff.invest.schemas import AssetsRequest, InstrumentStatus, InstrumentType

# TOKEN = os.environ["INVEST_TOKEN"]


# async def main():
#     async with AsyncClient(TOKEN) as client:
#         r = await client.instruments.get_assets()
#         print("BASE SHARE ASSETS")
#         for bond in r.assets:
#             print(bond)


# if __name__ == "__main__":
#     asyncio.run(main())

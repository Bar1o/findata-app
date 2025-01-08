from tinkoff.invest.schemas import IndicativesRequest

import os
import json
from tinkoff.invest import Client
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ["INVEST_TOKEN"]

data = []


def main():
    with Client(TOKEN) as client:
        request = IndicativesRequest()
        indicatives = client.instruments.indicatives(request=request)
        for instrument in indicatives.instruments:
            print(instrument.name, instrument.ticker, instrument.figi)


if __name__ == "__main__":
    main()

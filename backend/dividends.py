import os
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from tinkoff.invest import Client
from tinkoff.invest.schemas import GetDividendsRequest
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        from_date = datetime.strptime("07-01-2024", "%d-%m-%Y")
        to_date = datetime.strptime("07-01-2025", "%d-%m-%Y")

        dividends = client.instruments.get_dividends(figi="TCS00A107T19", from_=from_date, to=to_date)
        for div in dividends.dividends:
            print(div)


if __name__ == "__main__":
    main()

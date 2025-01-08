import os
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from tinkoff.invest import Client
from tinkoff.invest.schemas import GetAssetFundamentalsRequest, AssetShare
from tinkoff.invest.schemas import AssetsRequest, InstrumentStatus, InstrumentType
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.environ["INVEST_TOKEN"]


def main():
    with Client(TOKEN) as client:
        assets = client.instruments.get_asset_by(id="40d89385-a03a-4659-bf4e-d3ecba011782")
        print(assets)


if __name__ == "__main__":
    main()

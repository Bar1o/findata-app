from pydantic import BaseModel, Field
from datetime import datetime
from pandas import DataFrame
import pandas as pd
import json


class PaperData(BaseModel):
    """class handles tables for paper and returns data on ticker"""

    model_config = {"arbitrary_types_allowed": True}

    # ticker: str = None
    # figi: str = None
    # isin: str = None
    # nominal_price: int
    # currency: str
    # listing_level: int
    # volume: int
    # lot: int
    # trade_start_data: datetime

    main_data: DataFrame = Field(default_factory=DataFrame)
    dividend_data: dict = Field(default_factory=dict)

    ################# service variables #####################
    asset_data: DataFrame = Field(default_factory=DataFrame)
    #########################################################

    def __init__(self, **main_data):
        super().__init__(**main_data)
        if self.main_data.empty:
            self.main_data = self.get_assets_table()

    def get_assets_table(self):
        """Return a consolidated table of assets info
        including uid, name and nested instrument main_data:
        figi, ticker, class_code"""

        import os
        from tinkoff.invest import Client
        from tinkoff.invest.schemas import InstrumentStatus, InstrumentType

        TOKEN = os.environ["INVEST_TOKEN"]

        rows = []
        with Client(TOKEN) as client:
            r = client.instruments.get_assets()
            for asset in r.assets:
                asset_data = {
                    "uid": getattr(asset, "uid", None),
                    "name": getattr(asset, "name", None),
                }
                instruments = getattr(asset, "instruments", [])
                if instruments:
                    instr = instruments[0]
                    asset_data.update(
                        {
                            "figi": getattr(instr, "figi", None),
                            "ticker": getattr(instr, "ticker", None),
                            "class_code": getattr(instr, "class_code", None),
                        }
                    )
                rows.append(asset_data)

        return DataFrame(rows)

    def get_uid_by_ticker(self, ticker: str) -> str | None:
        row = self.main_data[self.main_data["ticker"] == ticker]
        if not row.empty:
            return row.iloc[0]["uid"]
        return None

    def get_figi_by_ticker(self, ticker: str) -> str | None:
        row = self.main_data[self.main_data["ticker"] == ticker]
        if not row.empty:
            return row.iloc[0]["figi"]
        return None

    def get_asset_data_by_ticker(self, ticker: str) -> DataFrame:
        """
        Retrieve asset data by uid from the API,
        extract the 'security' table (isin and share info).
        """
        import os
        from tinkoff.invest import Client
        from dotenv import load_dotenv

        load_dotenv()
        TOKEN = os.environ["INVEST_TOKEN"]

        asset = []

        with Client(TOKEN) as client:
            uid = self.get_uid_by_ticker(ticker)
            assets = client.instruments.get_asset_by(id=uid)
            asset.append(assets)

        assdf = DataFrame(list(DataFrame(asset)["asset"]))
        list_data = list(assdf["security"])  # isin, share are here
        return list_data

    def export_main_data_json(self, ticker: str) -> json:
        """Look up the corresponding 'ticker' and 'figi'
        and join them with share data to return a JSON."""

        columns = [
            "issue_size",
            "nominal",
            "nominal_currency",
            "primary_index",
            "preferred_share_type",
            "ipo_date",
            "registry_date",
            "issue_kind",
            "placement_date",
            "repres_isin",
            "issue_size_plan",
            "total_float",
        ]

        dividend_columns = ["dividend_rate", "div_yield_flag"]

        if self.asset_data.empty:
            self.asset_data = self.get_asset_data_by_ticker(ticker)

        list_data = self.asset_data
        figi = self.get_figi_by_ticker(ticker)

        res = {}
        divs_res = {}

        divs_res["ticker"] = ticker
        res["ticker"] = ticker
        res["figi"] = figi
        res["isin"] = list_data[0]["isin"]

        shares = list_data[0]["share"]
        for el in shares:
            if el in columns:
                res[el] = shares[el]
            elif el in dividend_columns:
                divs_res[el] = shares[el]

        self.dividend_data = divs_res
        return {"main_data": res}


print(PaperData().export_main_data_json(ticker="SBER"))

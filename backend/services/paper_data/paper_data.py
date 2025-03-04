from pydantic import BaseModel, Field
from datetime import datetime
from pandas import DataFrame
import pandas as pd
import json

from models.models import convert_quotation, Quotation

from .total_tickers import api_tickers


class PaperData(BaseModel):
    """Handles tables with main paper data (share main info) and returns data on ticker"""

    model_config = {"arbitrary_types_allowed": True}
    main_data: DataFrame = Field(default_factory=DataFrame)
    dividend_data: dict = Field(default_factory=dict)  # TODO: remove as not necessary

    ################# service variables #####################
    asset_data: DataFrame = Field(default_factory=DataFrame)
    #########################################################

    def __init__(self, **main_data):
        super().__init__(**main_data)
        if self.main_data.empty:
            self.main_data = self.get_assets_table()

    def get_assets_table(self) -> DataFrame:
        """Return a consolidated table of assets info
        => columns [uid, name, figi, ticker, class_code]"""

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
        assets_table = DataFrame(rows)
        asstable = assets_table.loc[assets_table["ticker"].isin(api_tickers)]
        return asstable

    # service methods
    #################################################################

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
        Func to get data from API.

        Returns RAW asset data
        from big asset table (gets tech share info) by 'uid' from the API,
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

    ###############################################################

    def export_main_data_json_by_ticker(self, ticker: str) -> json:
        """
        Formats data to get a JSON. Returs JSON.

        Work logic:
        + get_asset_data_by_ticker
        + get_uid_by_ticker
        + get_figi_by_ticker
        -> format => JSON.

        Look up the corresponding 'ticker' and 'figi'
        and join them with share data to return a JSON.
        """

        def to_convert(el) -> bool:
            list_to_convert = ["issue_size", "issue_size_plan", "nominal", "total_float"]
            if el in list_to_convert:
                return True
            return False

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
            conv_shares_el = shares[el]
            if to_convert(el):
                conv_shares_el = convert_quotation(Quotation(**conv_shares_el))

            if el in columns:
                res[el] = conv_shares_el
            elif el in dividend_columns:
                divs_res[el] = conv_shares_el

        self.dividend_data = divs_res
        return {"mainData": res}


# print(PaperData().export_main_data_json_by_ticker(ticker="SBER"))

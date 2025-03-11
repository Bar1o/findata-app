# python -m services.paper_data.paper_data
from pydantic import BaseModel, Field
from datetime import datetime
from pandas import DataFrame
import pandas as pd
from dotenv import load_dotenv
import json
from tinkoff.invest import Client, InstrumentIdType, AssetResponse
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("INVEST_TOKEN")

from models.models import convert_quotation, Quotation

from .total_tickers import api_tickers


class PaperData(BaseModel):
    """Handles tables with main paper data (share main info) and returns data on ticker"""

    model_config = {"arbitrary_types_allowed": True}

    ################# service variables #####################
    asset_data: DataFrame = Field(default_factory=DataFrame)
    #########################################################

    ################# main methods (only they're to use) ###############
    def get_uid_ticker_figi_data_by_ticker(self, ticker: str) -> dict:
        """
        Returns uid-ticker-figi dict from T-api for all tickers.
        Used in TickerTableDBManager.
        """
        with Client(TOKEN) as client:
            instruments = client.instruments.find_instrument(query=ticker)
            for instrument in instruments.instruments:
                if instrument.ticker == ticker:
                    details = client.instruments.get_instrument_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                        class_code="TQBR",  # класс акций Московской биржи
                        id=instrument.ticker,
                    )
                    logger.debug(f"uid-ticker-figi:{details.instrument.ticker}")

                    return {
                        "ticker": details.instrument.ticker,
                        "figi": details.instrument.figi,
                        "isin": details.instrument.isin,
                        "uid": details.instrument.asset_uid,
                        "currency": details.instrument.currency,
                    }
        return None

    def get_main_data_on_share_by_uid(self, uid: str) -> dict:
        """
        Returns paper main data by uid.
        Used in PaperDataDBManager.
        """
        # uid = "4b449b8c-7433-479f-9cad-53aa8226a28c"
        with Client(TOKEN) as client:

            asset_response: AssetResponse = client.instruments.get_asset_by(id=uid)
            res = asset_response.asset
            seq = res.security.share
            inst = None
            for el in res.instruments:
                if el.class_code == "TQBR":
                    inst = el
            logger.debug(f"class_code is TQBR:{inst.class_code=="TQBR",inst.class_code}")
            final = {
                "ticker": inst.ticker,
                "figi": inst.figi,
                "isin": res.security.isin,
                "issue_size": convert_quotation(Quotation(units=seq.issue_size.units, nano=seq.issue_size.nano)),
                "nominal": convert_quotation(Quotation(units=seq.nominal.units, nano=seq.nominal.nano)),
                "nominal_currency": seq.nominal_currency,
                "primary_index": seq.primary_index,
                "preferred_share_type": seq.preferred_share_type,
                "ipo_date": seq.ipo_date,
                "registry_date": seq.registry_date,
                "issue_kind": seq.issue_kind,
                "placement_date": seq.placement_date,
                "repres_isin": seq.repres_isin,
                "issue_size_plan": convert_quotation(Quotation(units=seq.issue_size_plan.units, nano=seq.issue_size_plan.nano)),
                "total_float": convert_quotation(Quotation(units=seq.total_float.units, nano=seq.total_float.nano)),
            }
            logger.debug(f"get_final")

            return final


data = PaperData()
print(PaperData().get_main_data_on_share_by_uid("4393bdb6-9017-466e-a3bb-ddb55d24159f"))

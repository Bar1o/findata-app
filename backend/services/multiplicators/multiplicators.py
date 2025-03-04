# python -m services.multiplicators.multiplicators
import os
from typing import List, Dict, Any

from tinkoff.invest import Client
from tinkoff.invest.schemas import GetAssetFundamentalsRequest
from ..paper_data.paper_data_db import PaperDataDBManager
from ..paper_data.total_tickers import api_tickers

TOKEN = os.environ["INVEST_TOKEN"]


# сделать импорт таблицы со всеми figi-uid
db_manager = PaperDataDBManager()
assets_data = db_manager.check_assets_table()

# взять uid по figi для каждого ticker из api_tickers используя assets_data
# тем самым получив list of assets и через этот list делать запрос в get_multiplicator_data_by_figi


def get_asset_uids(tickers: List[str] = api_tickers) -> List[str]:
    """
    Get UIDs for the specified tickers (api_tickers) using assets_data
    """
    uids = []
    for ticker in tickers:
        # Find the row for this ticker in assets_data
        ticker_row = assets_data[assets_data["ticker"] == ticker]
        if not ticker_row.empty:
            uid = ticker_row.iloc[0]["uid"]
            if uid:  # Skip empty UIDs
                uids.append(uid)
    return uids


def get_multiplicator_data_by_figi(figi: str):
    """
    Works only for tickers in api_tickers
    """
    result = []
    with Client(TOKEN) as client:
        request = GetAssetFundamentalsRequest(
            # assets=["40d89385-a03a-4659-bf4e-d3ecba011782"],
            assets=get_asset_uids()
        )
        result.append(client.instruments.get_asset_fundamentals(request=request))
    # здесь через мапу перейти к json


print(len(get_asset_uids()))

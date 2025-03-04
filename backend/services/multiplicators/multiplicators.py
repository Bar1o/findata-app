# python -m services.multiplicators.multiplicators
import os
from typing import List, Dict, Any

from tinkoff.invest import Client
from tinkoff.invest.schemas import GetAssetFundamentalsRequest
from ..paper_data.paper_data_db import PaperDataDBManager
from ..paper_data.total_tickers import api_tickers
import json

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


def get_multiplicator_data_from_api():
    """
    Works only for tickers in api_tickers
    (=> 9 без тинька — его нет; щас вроде
    уже T-Технологии отдельно торгуются)

    Fetches the fundamentals for all assets in the list (obtained via get_asset_uids)
    and returns a dictionary with the ticker as key and the corresponding data as value.
    """
    all_results = {}
    with Client(TOKEN) as client:
        request = GetAssetFundamentalsRequest(
            # assets=["40d89385-a03a-4659-bf4e-d3ecba011782"],
            assets=get_asset_uids()
        )
        response = client.instruments.get_asset_fundamentals(request=request)

        for res in response.fundamentals:
            ticker_rows = assets_data[assets_data["uid"] == res.asset_uid]
            ticker = ticker_rows.iloc[0]["ticker"] if not ticker_rows.empty else res.asset_uid

            all_results[ticker] = {
                "market_capitalization": res.market_capitalization,
                "ticker": ticker,
                "currency": res.currency,
                "high_price_last_52_weeks": res.high_price_last_52_weeks,
                "low_price_last_52_weeks": res.low_price_last_52_weeks,
                "average_daily_volume_last_10_days": res.average_daily_volume_last_10_days,
                "average_daily_volume_last_4_weeks": res.average_daily_volume_last_4_weeks,
                "beta": res.beta,
                "free_float": res.free_float,
                "forward_annual_dividend_yield": res.forward_annual_dividend_yield,
                "shares_outstanding": res.shares_outstanding,
                "revenue_ttm": res.revenue_ttm,
                "ebitda_ttm": res.ebitda_ttm,
                "net_income_ttm": res.net_income_ttm,
                "eps_ttm": res.eps_ttm,
                "pe_ratio_ttm": res.pe_ratio_ttm,
                "price_to_sales_ttm": res.price_to_sales_ttm,
                "price_to_book_ttm": res.price_to_book_ttm,
                "total_enterprise_value_mrq": res.total_enterprise_value_mrq,
                "ev_to_ebitda_mrq": res.ev_to_ebitda_mrq,
                "roe": res.roe,
                "roa": res.roa,
                "roic": res.roic,
                "total_debt_to_equity_mrq": res.total_debt_to_equity_mrq,
                "total_debt_to_ebitda_mrq": res.total_debt_to_ebitda_mrq,
                "dividend_yield_daily_ttm": res.dividend_yield_daily_ttm,
                "current_ratio_mrq": res.current_ratio_mrq,
                "dividend_rate_ttm": res.dividend_rate_ttm,
                "dividends_per_share": res.dividends_per_share,
                "five_years_average_dividend_yield": res.five_years_average_dividend_yield,
                "dividend_payout_ratio_fy": res.dividend_payout_ratio_fy,
                "buy_back_ttm": res.buy_back_ttm,
                "one_year_annual_revenue_growth_rate": res.one_year_annual_revenue_growth_rate,
                "revenue_change_five_years": res.revenue_change_five_years,
                "eps_change_five_years": res.eps_change_five_years,
                "ev_to_sales": res.ev_to_sales,
                "ex_dividend_date": res.ex_dividend_date,
            }
    return all_results


# result = get_multiplicator_data_from_api()
# print(json.dumps(result, default=str, indent=2))

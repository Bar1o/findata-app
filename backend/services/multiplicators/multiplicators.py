# python -m services.multiplicators.multiplicators

import os
import logging
from typing import List, Dict, Any
from tinkoff.invest import Client
from tinkoff.invest.schemas import GetAssetFundamentalsRequest
from ..paper_data.ticker_table_db import TickerTableDBManager
from ..paper_data.total_tickers import all_tickers
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Multiplicators:
    """
    Класс для получения данных мультипликаторов фондовых показателей.
    Содержит методы для:
      - конвертации данных из API (масштабирование, форматирование),
      - получения мультипликаторных данных для всех активов,
      - получения дивидендных данных для отдельного тикера.
    """

    def __init__(self):
        self.token = os.environ.get("INVEST_TOKEN")
        self.db_manager = TickerTableDBManager()

    def get_asset_uids(self, tickers: List[str] = all_tickers) -> List[str]:
        """
        Возвращает список uid активов для заданных тикеров.
        """
        uids = []
        for ticker in tickers:
            uid = self.db_manager.get_uid_by_ticker(ticker)
            uids.append(uid)
        logger.debug("get_asset_uids выполнен")
        return uids

    def convert_api_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Конвертирует данные из API с масштабированием значений и добавлением единиц измерения.
        """
        unit_mapping = {
            "market_capitalization": ("млрд руб", 1e9),
            "ticker": ("", 1),
            "currency": ("", 1),
            "high_price_last_52_weeks": ("руб", 1),
            "low_price_last_52_weeks": ("руб", 1),
            "average_daily_volume_last_10_days": ("шт", 1),
            "average_daily_volume_last_4_weeks": ("шт", 1),
            "beta": ("", 1),
            "free_float": ("%", 1),
            "forward_annual_dividend_yield": ("%", 1),
            "shares_outstanding": ("млн", 1e6),
            "revenue_ttm": ("млрд руб", 1e9),
            "ebitda_ttm": ("млрд руб", 1e9),
            "net_income_ttm": ("млрд руб", 1e9),
            "eps_ttm": ("руб", 1),
            "pe_ratio_ttm": ("", 1),
            "price_to_sales_ttm": ("", 1),
            "price_to_book_ttm": ("", 1),
            "total_enterprise_value_mrq": ("млрд руб", 1e9),
            "ev_to_ebitda_mrq": ("", 1),
            "roe": ("%", 1),
            "roa": ("%", 1),
            "roic": ("%", 1),
            "total_debt_to_equity_mrq": ("", 1),
            "total_debt_to_ebitda_mrq": ("", 1),
            "current_ratio_mrq": ("", 1),
            "five_years_average_dividend_yield": ("%", 1),
            "dividend_payout_ratio_fy": ("%", 1),
            "buy_back_ttm": ("млрд руб", 1e9),
            "one_year_annual_revenue_growth_rate": ("%", 1),
            "revenue_change_five_years": ("%", 1),
            "eps_change_five_years": ("%", 1),
            "ev_to_sales": ("", 1),
            "ex_dividend_date": ("", 1),
        }
        result = {}
        for key, value in api_data.items():
            if key in unit_mapping and value is not None:
                unit, divisor = unit_mapping[key]
                if isinstance(value, str):
                    formatted_value = value
                elif isinstance(value, (int, float)):
                    if divisor == 1:
                        formatted_value = str(value) if isinstance(value, int) else f"{value:.2f}"
                    else:
                        formatted_value = f"{value / divisor:,.0f}".replace(",", " ")
                else:
                    formatted_value = str(value)
                result[key] = {"value": formatted_value, "unit": unit}
        return result

    def get_multiplicator_data_from_api(self) -> Dict[str, Any]:
        """
        Получает данные мультипликаторов для всех активов через API.
        Возвращает словарь, где ключ – тикер, значение – конвертированные данные.
        """
        mult_res = {}
        conv_multip_res = {}
        with Client(self.token) as client:
            request = GetAssetFundamentalsRequest(assets=self.get_asset_uids())
            response = client.instruments.get_asset_fundamentals(request=request)
            for res in response.fundamentals:
                ticker = self.db_manager.get_ticker_by_uid(res.asset_uid)
                mult_res[ticker] = {
                    "market_capitalization": res.market_capitalization,
                    "ticker": ticker,
                    "currency": res.currency,
                    "high_price_last_52_weeks": res.high_price_last_52_weeks,
                    "low_price_last_52_weeks": res.low_price_last_52_weeks,
                    "average_daily_volume_last_10_days": res.average_daily_volume_last_10_days,
                    "average_daily_volume_last_4_weeks": res.average_daily_volume_last_4_weeks,
                    "beta": res.beta,
                    "free_float": res.free_float,
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
                    "buy_back_ttm": res.buy_back_ttm,
                    "one_year_annual_revenue_growth_rate": res.one_year_annual_revenue_growth_rate,
                    "revenue_change_five_years": res.revenue_change_five_years,
                    "eps_change_five_years": res.eps_change_five_years,
                    "ev_to_sales": res.ev_to_sales,
                    "ex_dividend_date": res.ex_dividend_date,
                }
                logger.debug(f"mult_res: {mult_res}")
                conv_multip_res[ticker] = self.convert_api_data(mult_res[ticker])
        logger.debug(f"conv_multip_res: {conv_multip_res}")
        return conv_multip_res

    def get_divs_from_multiplicator_data_from_api(self, ticker: str) -> Dict[str, Any]:
        """
        Используется для получения данных по дивидендам для указанного тикера
        через API мультипликаторов.
        """
        divs_res = {}
        conv_divs_res = {}
        uid = self.db_manager.get_uid_by_ticker(ticker)
        with Client(self.token) as client:
            request = GetAssetFundamentalsRequest(assets=[uid])
            response = client.instruments.get_asset_fundamentals(request=request)
            for res in response.fundamentals:
                divs_res = {
                    "current_ratio_mrq": res.current_ratio_mrq,
                    "five_years_average_dividend_yield": res.five_years_average_dividend_yield,
                    "dividend_payout_ratio_fy": res.dividend_payout_ratio_fy,
                    "forward_annual_dividend_yield": res.forward_annual_dividend_yield,
                }
                conv_divs_res = self.convert_api_data(divs_res)
        return conv_divs_res

# python -m services.multiplicators.parse_multipl
from bs4 import BeautifulSoup
import requests
import json
import requests
import re
from datetime import datetime
from ..paper_data.total_tickers import missing_tickers


def parse_financial_data(ticker: str, target_year: int = datetime.now().year):
    url = f"https://smart-lab.ru/q/{ticker}/f/y/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"class": "simple-little-table financials"})
    if not table:
        print(f"Table not found for {ticker}")
        return {"ticker": ticker, "error": "Financial table not found"}

    result = {
        "year": None,  # чтобы занть какой год был взят
        "market_capitalization": None,
        "ticker": None,
        "currency": "RUB",
        # "high_price_last_52_weeks": None,
        # "low_price_last_52_weeks": None,
        # "average_daily_volume_last_10_days": None,
        # "average_daily_volume_last_4_weeks": None,
        # "beta": None,
        # "free_float": None,
        "forward_annual_dividend_yield": None,
        "shares_outstanding": None,
        "revenue_ttm": None,
        "ebitda_ttm": None,
        "net_income_ttm": None,
        "eps_ttm": None,
        "pe_ratio_ttm": None,
        "price_to_sales_ttm": None,
        "price_to_book_ttm": None,
        "price_to_book_value_ttm": None,
        "total_enterprise_value_mrq": None,
        "ev_to_ebitda_mrq": None,
        "roe": None,
        "roa": None,
        # "roic": None,
        # "total_debt_to_equity_mrq": None,
        "total_debt_to_ebitda_mrq": None,
        # "dividend_yield_daily_ttm": None,
        # "current_ratio_mrq": None,
        # "dividend_rate_ttm": None,
        "dividends_per_share": None,
        # "five_years_average_dividend_yield": None,
        "dividend_payout_ratio_fy": None,
        # "buy_back_ttm": None,
        # "one_year_annual_revenue_growth_rate": None,
        # "revenue_change_five_years": None,
        # "eps_change_five_years": None,
        # "ev_to_sales": None,
        # "ex_dividend_date": None,
    }

    year_columns = {}
    header_row = table.find("tr", {"class": "header_row"})
    if header_row:
        for idx, td in enumerate(header_row.find_all("td")):
            year = td.get_text(strip=True)
            if year.isdigit():
                year_columns[int(year)] = idx
            else:  # for LTM
                year_columns[year[:-1]] = idx

    possible_periods = [target_year, target_year - 1, "LTM"]
    for period in possible_periods:
        target_year = period
        year_idx = year_columns.get(target_year)
        if year_idx:
            break

    if year_idx is None:
        raise Exception("can't get data — no period (targer_year)")

    result["year"] = target_year
    result["ticker"] = ticker

    # Маппинг полей, которые будут в итоговом json
    # IMPORTANT: абсолютные значения — млрд руб (на фронте отобразить подпись млрд)

    field_mapping = {
        "market_cap": ("market_capitalization", "млрд руб"),
        "free_float": ("free_float", "%"),
        "div_yield": ("forward_annual_dividend_yield", "%"),
        "number_of_shares": ("shares_outstanding", "млн"),
        "revenue": ("revenue_ttm", "млрд руб"),
        "ebitda": ("ebitda_ttm", "млрд руб"),
        "net_income": ("net_income_ttm", "млрд руб"),
        "eps": ("eps_ttm", "руб"),
        "p_e": ("pe_ratio_ttm", ""),
        "p_s": ("price_to_sales_ttm", ""),
        "p_bv": ("price_to_book_value_ttm", ""),
        "p_b": ("price_to_book_ttm", ""),
        "ev": ("total_enterprise_value_mrq", "млрд руб"),
        "ev_ebitda": ("ev_to_ebitda_mrq", ""),
        "roe": ("roe", "%"),
        "roa": ("roa", "%"),
        "dividend": ("dividends_per_share", "руб"),
        "div_payout_ratio": ("dividend_payout_ratio_fy", "%"),
        "debt_ebitda": ("total_debt_to_ebitda_mrq", ""),
    }

    # Парсинг данных
    for field, (target, default_unit) in field_mapping.items():
        row = table.find("tr", {"field": field})
        if row:
            # Извлечение единиц измерения из заголовка
            unit = default_unit
            header = row.find("th")
            if header:
                unit_span = header.find("span")
                if unit_span:
                    unit = unit_span.get_text(strip=True).replace(",", "").replace("(", "").replace(")", "")

            # Извлечение значения
            tds = row.find_all("td")
            if len(tds) > year_idx:
                value = tds[year_idx].get_text(strip=True)
                cleaned_value = value.replace(" ", "").replace(",", ".").replace("%", "")

                # Формирование структуры данных
                result[target] = {"value": cleaned_value if cleaned_value else None, "unit": unit.strip() or default_unit}

    return result


# def get_parsed_financial_data() -> dict[dict[str]]:
#     all_results = dict()
#     for ticker in missing_tickers:
#         all_results[ticker] = parse_financial_data(ticker)

#     return all_results


# print(json.dumps(get_parsed_financial_data(), default=str, indent=2))

# print(parse_financial_data("T"))

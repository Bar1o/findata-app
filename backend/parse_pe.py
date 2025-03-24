import json
from bs4 import BeautifulSoup
import pandas as pd
import requests
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from services.paper_data.total_tickers import tech, retail, banks, build, oil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParsePE(BaseModel):
    """
    Class to parse P/E data from smart-lab.ru for tickers and sectors.

    example:
    sector_tickers_pe = {"tech":{
        "SBER": {
            "year":[2020, 2021],
            "P/E": [10.97, 11.11],
            "year_change": [0.75, 0.33]
        }
    }}
    """

    sector_tickers: dict = {"tech": tech, "retail": retail, "banks": banks, "build": build, "oil": oil}
    sector_tickers_pe: dict = {}

    def parse_pe_by_ticker(self, ticker: str) -> dict:
        """
        Fetch and parse P/E data for a specific ticker.

        Returns dictionary with year, P/E values, and year-over-year changes
        """
        logger.info(f"Fetching P/E data for ticker: {ticker}")

        try:
            url = f"https://smart-lab.ru/q/{ticker}/MSFO/p_e/"
            response = requests.get(url)
            response.raise_for_status()
            html = response.text

            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", {"class": "simple-little-table financials"})

            if not table:
                logger.error(f"Cannot find P/E table for ticker {ticker}")
                return {"year": [], "P/E": [], "year_change": []}

            header_row = table.find("tr", {"class": "header_row"})
            years = []
            if header_row:
                header_cells = header_row.find_all("td")
                for cell in header_cells:
                    strong = cell.find("strong")
                    if strong:
                        text = strong.get_text(strip=True)
                        if text.isdigit():
                            years.append(int(text))

                years = years[:]

            pe_row = None
            for row in table.find_all("tr"):
                ths = row.find_all("th")
                if ths and ths[0].get_text(strip=True) == "P/E":
                    pe_row = row
                    break

            pe_values = []
            if pe_row:
                cells = pe_row.find_all("td")
                for cell in cells[: len(years)]:
                    cell_text = cell.get_text(strip=True)
                    try:
                        val = float(cell_text.replace(",", "."))
                    except ValueError:
                        val = None
                    pe_values.append(val)

            change_row = None
            for row in table.find_all("tr"):
                th = row.find("th")
                if th and "Изм. за год" in th.get_text():
                    change_row = row
                    break

            year_changes = []
            if change_row:
                cells = change_row.find_all("td")
                for cell in cells[: len(years)]:
                    text = cell.get_text(strip=True)
                    if text.endswith("%"):
                        try:
                            numeric = float(text.replace("%", "").replace("+", ""))
                            if "-" in text:
                                numeric = -abs(numeric)
                            year_changes.append(round(numeric / 100, 2))
                        except ValueError:
                            year_changes.append(None)
                    else:
                        year_changes.append(None)

            return {
                "year": years,
                "P/E": pe_values,
                "year_change": year_changes,
            }

        except Exception as e:
            logger.error(f"Error fetching P/E data for {ticker}: {e}")
            return {"year": [], "P/E": [], "year_change": []}

    def parse_pe_by_sector(self, sector: str):
        """
        Get P/E data for all tickers in a specified sector.
        """
        sector = sector.lower()

        if sector not in self.sector_tickers:
            raise ValueError(f"Invalid sector: {sector}. Choose from: tech, retail, banks, build, oil")

        tickers = self.sector_tickers[sector]
        logger.info(f"Fetching P/E data for {len(tickers)} tickers in {sector} sector")

        result = {}
        for ticker in tickers:
            logger.info(f"Processing ticker {ticker} for sector {sector}")
            pe_data = self.parse_pe_by_ticker(ticker)

            # Only include tickers with actual data
            if pe_data["year"] and any(pe_data["P/E"]):
                result[ticker] = pe_data
            else:
                logger.warning(f"No P/E data found for {ticker}")

        self.sector_tickers_pe[sector] = result

    def get_pe_by_sector(self, sector: str):
        data = self.sector_tickers_pe.get(sector)
        if data:
            return data

        self.parse_pe_by_sector(sector)
        return self.sector_tickers_pe[sector]

    def mean_pe_by_sector(self, sector: str) -> dict:
        """
        Calculate mean P/E values and year changes across a sector.

        Returns dictionary with mean P/E values and changes by year for the sector
        """
        # sector_data = self.sector_tickers_pe.get(sector)
        sector_data = self.get_pe_by_sector(sector)
        if not sector_data:
            sector_data = self.parse_pe_by_sector(sector)

        if not sector_data:
            logger.warning(f"No valid P/E data found for sector: {sector}")
            return {"year": [], "P/E": [], "year_change": []}

        all_years = set()
        for ticker_data in sector_data.values():
            all_years.update(ticker_data["year"])

        all_years = sorted(all_years)

        pe_sums = {year: 0.0 for year in all_years}
        pe_counts = {year: 0 for year in all_years}
        change_sums = {year: 0.0 for year in all_years}
        change_counts = {year: 0 for year in all_years}

        for ticker_data in sector_data.values():
            years = ticker_data["year"]
            pe_values = ticker_data["P/E"]
            year_changes = ticker_data["year_change"]

            for i, year in enumerate(years):
                if i < len(pe_values) and pe_values[i] is not None:
                    pe_sums[year] += pe_values[i]
                    pe_counts[year] += 1

                if i < len(year_changes) and year_changes[i] is not None:
                    change_sums[year] += year_changes[i]
                    change_counts[year] += 1

        # calculate means
        mean_pe = []
        mean_changes = []
        final_years = []

        for year in all_years:
            final_years.append(year)

            if pe_counts[year] > 0:
                mean_pe.append(round(pe_sums[year] / pe_counts[year], 2))
            else:
                mean_pe.append(None)

            if change_counts[year] > 0:
                mean_changes.append(round(change_sums[year] / change_counts[year], 2))
            else:
                mean_changes.append(None)

        return {"year": final_years, "P/E": mean_pe, "year_change": mean_changes}

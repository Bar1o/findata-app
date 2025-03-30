from pydantic import BaseModel
import pandas as pd
from pandas import DataFrame
import yfinance as yf
from datetime import datetime


class GdpData(BaseModel):
    """
    Извлекает данные из xlsx файлов Росстата.
    Начинается с 2011 года.
    """

    total_gdp_curr_prices: dict = {}
    sectors_gdp: dict = {}

    def __init__(self, **data):
        super().__init__(**data)

        self.total_gdp_curr_prices = self.extract_total_gdp()
        self.sectors_gdp = self.extract_sectors_gdp()

    ################### service functions ################
    def extract_total_gdp(self) -> dict:
        """
        Данные ВВП в абс. знач. в текущих ценах
        с 2011 по 2024
        """
        gdp_file_name = "VVP_god_s_1995-2024.xlsx"

        gdp_data = pd.read_excel(gdp_file_name, sheet_name="2", skiprows=3, skipfooter=3)
        rename_dict = {"20222)": 2022, "20232)": 2023, "20242)": 2024}
        gdp_data = gdp_data.rename(columns=rename_dict)
        gdp_total_abs = gdp_data.T
        gdp_total_abs = gdp_total_abs.rename(columns={0: "values"})
        gdp_total_abs.index = pd.to_numeric(gdp_total_abs.index, errors="coerce")
        gdp_total_abs = gdp_total_abs.dropna()
        return gdp_total_abs

    def extract_sectors_gdp(self) -> dict:
        """
        Индексы - дефляторы валового внутреннего продукта
        (в процентах к предыдущему году)
        с 2012 по 2024
        """
        gdp_data = pd.read_excel("VDS_god_OKVED2_s_2011-2024.xlsx", sheet_name="4", skiprows=2)
        rename_dict = {"20222)": 2022, "20232)": 2023, "20242)": 2024}
        gdp_data = gdp_data.rename(columns=rename_dict)

        sectors = {"tech": "Раздел J", "retail": "Раздел G", "banks": "Раздел K", "build": "Раздел F", "oil": "Раздел  В"}

        filtered_data = gdp_data[gdp_data["коды"].isin(sectors.values())]
        gdp_sectors = filtered_data.set_index("коды").T.iloc[2:]
        gdp_sectors.index = pd.to_numeric(gdp_sectors.index, errors="coerce").dropna()
        gdp_sectors = gdp_sectors.rename(columns={v: k for k, v in sectors.items()}).apply(pd.to_numeric)
        return gdp_sectors

    #################### main functions ################################
    def get_total_gdp(self, start: int | None = None, end: int | None = None) -> dict:
        """для IMOEX start year = 2013"""
        if start is None:
            start = 2011
        if end is None:
            end = datetime.now().year

        filtered_df = self.total_gdp_curr_prices.loc[start:end]

        result = {"gdp": [{"year": int(index), "value": float(row["values"])} for index, row in filtered_df.iterrows()]}
        return result

    def get_sectors_gdp(self, start: int | None = None, end: int | None = None) -> dict:
        df = self.sectors_gdp

        if start is None:
            start = 2012
        if end is None:
            end = datetime.now().year

        df = self.sectors_gdp.loc[start:end]

        result = {}
        for col in df.columns:
            key = col.lower()  # конвертируем в нижний регистр
            result[key] = [{"year": int(year), "value": float(row[col])} for year, row in df.iterrows()]

        return result

    def get_gdp_by_sector(self, sector: str, start: int | None = None, end: int | None = None) -> dict:
        df = self.sectors_gdp
        if start is None:
            start = 2012
        if end is None:
            end = datetime.now().year

        df = self.sectors_gdp.loc[start:end]

        result = {}
        result[sector] = [{"year": int(year), "value": float(row[sector])} for year, row in df.iterrows()]
        return result


class ImoexData(BaseModel):
    """
    Получает данные из API yfinance для IMOEX.
    Начинается с 2013 года.
    """

    imoex_data: dict = {}

    def __init__(self, **data):
        super().__init__(**data)

        self.imoex_data = self.get_imoex_dat_from_api()

    def get_imoex_dat_from_api(self):
        imoex = yf.download("IMOEX.ME", start="2011-01-01", end="2024-12-31")
        imoex_yearly = imoex.resample("YE").last()
        return imoex_yearly

    def get_imoex_data(self) -> dict:
        imoex_yearly = self.imoex_data
        imoex_yearly.columns = imoex_yearly.columns.get_level_values(0)
        imoex_yearly = imoex_yearly[["Close"]]

        result = {"imoex": []}
        for date, row in imoex_yearly.iterrows():
            result["imoex"].append({"year": date.year, "close": float(row["Close"])})

        return result


# gdp = GdpData()
# imoex = ImoexData()

# res = {"gdp": gdp.get_total_gdp(2013)["gdp"], "imoex": imoex.get_imoex_data()["imoex"]}
# print(res)

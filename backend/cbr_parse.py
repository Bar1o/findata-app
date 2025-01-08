import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

header_mapping = {
    "Дата": "date",
    "Ключевая ставка, % годовых": "keyRate",
    "Инфляция, % г/г": "infl",
    "Цель по инфляции, %": "targetInfl",
}


def fetch_inflation_table():
    url = "https://www.cbr.ru/hd_base/infl/"
    response = requests.get(url)

    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch data. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", class_="data")
    if table is None:
        raise ValueError("Table with class 'data' not found.")

    headers = [header_mapping.get(th.text.strip(), th.text.strip()) for th in table.find("tr").find_all("th")]

    rows = []

    for row in table.find_all("tr")[1:]:  # пропуск заголовков
        cols = [td.text.strip() for td in row.find_all("td")]
        row_dict = dict(zip(headers, cols))

        for key, value in row_dict.items():
            if key.lower() == "date":
                continue
            else:
                row_dict[key] = float(value.replace(",", "."))

        rows.append(row_dict)

    return rows

    # json_data = json.dumps(rows, ensure_ascii=False, indent=4)
    # return json_data


try:
    inflation_data = fetch_inflation_table()
    logger.debug(inflation_data)
except Exception as e:
    logger.error(f"Error: {e}")

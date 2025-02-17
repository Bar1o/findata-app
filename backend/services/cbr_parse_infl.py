import requests
from bs4 import BeautifulSoup
import json
import logging
import pandas as pd
from sqlalchemy.orm import Session
from models.db_model import InflationTable, SessionLocal
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

header_mapping = {
    "Дата": "date",
    "Ключевая ставка, % годовых": "keyRate",
    "Инфляция, % г/г": "infl",
    "Цель по инфляции, %": "targetInfl",
}


def row_to_dict(row):
    return {
        "date": row.date,
        "keyRate": row.keyRate,
        "infl": row.infl,
        "targetInfl": row.targetInfl,
        # "last_updated": row.last_updated.isoformat(),
    }


def fetch_inflation_table():
    db: Session = SessionLocal()
    # check if data is recent (e.g., within the last 7 days)
    recent_data = db.query(InflationTable).filter(InflationTable.last_updated >= datetime.now() - timedelta(days=7)).all()

    if recent_data:
        return {"inflTable": [row_to_dict(row) for row in recent_data]}

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

        # Save to database
        db_row = InflationTable(
            date=row_dict["date"],
            keyRate=row_dict["keyRate"],
            infl=row_dict["infl"],
            targetInfl=row_dict["targetInfl"],
            last_updated=datetime.now(),
        )
        db.merge(db_row)
    db.commit()
    db.close()

    return {"inflTable": rows}


# try:
#     inflation_data = fetch_inflation_table()
#     logger.debug(inflation_data)
# except Exception as e:
#     logger.error(f"Error: {e}")

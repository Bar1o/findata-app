# python -m services.cbr_parse_infl
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json
import logging
import pandas as pd
from sqlalchemy.orm import Session
from models.db_model import InflationTable, SessionLocal

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

header_mapping = {
    "Дата": "date",
    "Ключевая ставка, % годовых": "keyRate",
    "Инфляция, % г/г": "infl",
    "Цель по инфляции, %": "targetInfl",
}

# Кэшировать данные каждые 7 дней
CACHE_DURATION = timedelta(days=7)


def row_to_dict(row):
    return {
        "date": row.date,
        "keyRate": row.keyRate,
        "infl": row.infl,
        "targetInfl": row.targetInfl,
    }


def fetch_inflation_table():
    db: Session = SessionLocal()

    # Если в базе есть хотя бы одна запись и они свежие, возвращаем кэш
    latest_record = db.query(InflationTable).order_by(InflationTable.last_updated.desc()).first()
    if latest_record and (datetime.now() - latest_record.last_updated) < CACHE_DURATION:
        logger.debug("Данные актуальны, возвращаем кэш из БД")
        latest_records = db.query(InflationTable).order_by(InflationTable.date.desc()).limit(12).all()
        latest_records = sorted(latest_records, key=lambda r: r.date)
        result_list = [row_to_dict(rec) for rec in latest_records]
        db.close()
        return {"inflTable": result_list}

    # Если данных нет или они устарели, делаем HTTP запрос
    url = "https://www.cbr.ru/hd_base/infl/"
    response = requests.get(url)
    if response.status_code != 200:
        db.close()
        raise ConnectionError(f"Failed to fetch data. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="data")
    if table is None:
        db.close()
        raise ValueError("Table with class 'data' not found.")

    headers = [header_mapping.get(th.text.strip(), th.text.strip()) for th in table.find("tr").find_all("th")]
    rows = []

    for row in table.find_all("tr")[1:]:  # пропускаем заголовок
        cols = [td.text.strip() for td in row.find_all("td")]
        row_dict = dict(zip(headers, cols))

        # Преобразуем числовые значения
        for key, value in row_dict.items():
            if key.lower() == "date":
                continue
            else:
                row_dict[key] = float(value.replace(",", "."))
        rows.append(row_dict)

        # Проверяем, существует ли запись для данной даты
        existing = db.query(InflationTable).filter(InflationTable.date == row_dict["date"]).first()
        if existing:
            if (
                existing.keyRate != row_dict["keyRate"]
                or existing.infl != row_dict["infl"]
                or existing.targetInfl != row_dict["targetInfl"]
            ):
                existing.keyRate = row_dict["keyRate"]
                existing.infl = row_dict["infl"]
                existing.targetInfl = row_dict["targetInfl"]
                existing.last_updated = datetime.now()
                db.add(existing)
        else:
            new_row = InflationTable(
                date=row_dict["date"],
                keyRate=row_dict["keyRate"],
                infl=row_dict["infl"],
                targetInfl=row_dict["targetInfl"],
                last_updated=datetime.now(),
            )
            db.add(new_row)

    db.commit()

    # Очистка: если данных больше 180, удаляем старые записи
    total_count = db.query(InflationTable).count()
    if total_count > 180:
        num_to_delete = total_count - 180
        old_records = db.query(InflationTable).order_by(InflationTable.date.asc()).limit(num_to_delete).all()
        for rec in old_records:
            db.delete(rec)
        db.commit()

    latest_records = db.query(InflationTable).order_by(InflationTable.date.desc()).limit(12).all()
    latest_records = sorted(latest_records, key=lambda r: r.date)
    result_list = [row_to_dict(rec) for rec in latest_records]
    db.close()

    return {"inflTable": result_list}


if __name__ == "__main__":
    try:
        inflation_data = fetch_inflation_table()
        logger.debug(inflation_data)
    except Exception as e:
        logger.error(f"Error: {e}")

from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import logging
from sqlalchemy.orm import Session

from models.db_model import InflationTable, SessionLocal

logger = logging.getLogger(__name__)

# Маппинг заголовков таблицы
header_mapping = {
    "Дата": "date",
    "Ключевая ставка, % годовых": "keyRate",
    "Инфляция, % г/г": "infl",
    "Цель по инфляции, %": "targetInfl",
}


class InflTable:
    CACHE_DURATION = timedelta(days=7)

    def __init__(self):
        self.session: Session = SessionLocal()

    def parse_data(self):
        """
        Парсит данные с сайта ЦБ и возвращает список словарей с данными.
        """
        url = "https://www.cbr.ru/hd_base/infl/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch data. Status code: {response.status_code}")
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", class_="data")
        if table is None:
            raise ValueError("Table with class 'data' not found.")
        headers_list = [header_mapping.get(th.text.strip(), th.text.strip()) for th in table.find("tr").find_all("th")]
        rows = []
        for row in table.find_all("tr")[1:]:  # пропускаем заголовок
            cols = [td.text.strip() for td in row.find_all("td")]
            row_dict = dict(zip(headers_list, cols))
            # Преобразуем числовые значения
            for key, value in row_dict.items():
                if key.lower() != "date":
                    try:
                        row_dict[key] = float(value.replace(",", "."))
                    except ValueError:
                        row_dict[key] = None
            rows.append(row_dict)
        return rows

    def add_data(self, rows):
        """
        Добавляет записи в БД, если их нет.
        """
        for row_dict in rows:
            existing = self.session.query(InflationTable).filter(InflationTable.date == row_dict["date"]).first()
            if not existing:
                new_row = InflationTable(
                    date=row_dict["date"],
                    keyRate=row_dict["keyRate"],
                    infl=row_dict["infl"],
                    targetInfl=row_dict["targetInfl"],
                    last_updated=datetime.now(),
                )
                self.session.add(new_row)
        self.session.commit()

    def update_data(self):
        """
        Обновляет данные в БД, если они устарели (старше 7 дней) или отсутствуют.
        Выполняется простейшая логика обновления: если запись есть, обновляем её, иначе создаём новую.
        Также производится очистка – если записей больше 180, удаляются самые старые.
        """
        latest_record = self.session.query(InflationTable).order_by(InflationTable.last_updated.desc()).first()
        if latest_record and (datetime.now() - latest_record.last_updated) < self.CACHE_DURATION:
            logger.debug("Данные актуальны – обновление не требуется")
        else:
            logger.debug("Обновление данных начато")
            rows = self.parse_data()
            for row_dict in rows:
                existing = self.session.query(InflationTable).filter(InflationTable.date == row_dict["date"]).first()
                if existing:
                    existing.keyRate = row_dict["keyRate"]
                    existing.infl = row_dict["infl"]
                    existing.targetInfl = row_dict["targetInfl"]
                    existing.last_updated = datetime.now()
                else:
                    new_row = InflationTable(
                        date=row_dict["date"],
                        keyRate=row_dict["keyRate"],
                        infl=row_dict["infl"],
                        targetInfl=row_dict["targetInfl"],
                        last_updated=datetime.now(),
                    )
                    self.session.add(new_row)
            self.session.commit()
            # Очистка старых записей, если их больше 180
            total_count = self.session.query(InflationTable).count()
            if total_count > 180:
                num_to_delete = total_count - 180
                old_records = self.session.query(InflationTable).order_by(InflationTable.date.asc()).limit(num_to_delete).all()
                for rec in old_records:
                    self.session.delete(rec)
                self.session.commit()
            logger.debug("Обновление данных завершено")

    def get_latest_data(self):
        """
        Возвращает последние 12 записей, отсортированные по возрастанию даты.
        """
        latest_records = self.session.query(InflationTable).order_by(InflationTable.date.desc()).limit(12).all()
        latest_records = sorted(latest_records, key=lambda r: r.date)
        result_list = []
        for rec in latest_records:
            result_list.append(
                {
                    "date": rec.date,
                    "keyRate": rec.keyRate,
                    "infl": rec.infl,
                    "targetInfl": rec.targetInfl,
                }
            )
        return result_list

    def delete_data(self):
        """
        Удаляет все записи из таблицы инфляции.
        """
        records = self.session.query(InflationTable).all()
        for rec in records:
            self.session.delete(rec)
        self.session.commit()

    def close(self):
        self.session.close()


# infl = InflTable()
# infl.update_data()
# print(infl.get_latest_data())

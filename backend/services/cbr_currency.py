# python -m services.cbr_currency
from pydantic import BaseModel
import requests
import xml.etree.ElementTree as ET
from datetime import date, datetime
from models.db_model import CurrencyRates, SessionLocal


class Currency(BaseModel):
    URL: str = "https://cbr.ru/scripts/XML_daily.asp"

    def get_api_data(self):
        """
        Использует cbr.ru URL и запрашивает XML с данными с сайта ЦБ.
        Дата запроса — сегодня.
        """
        today_str = date.today().strftime("%d/%m/%Y")
        url = f"{self.URL}?date_req={today_str}"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def parse_currency_data(self, xml_text):
        """
        Извлекает из XML курсы для USD, EUR и CNY.
        Для каждого элемента Valute берет значение Nominal и Value.
        Значение курса нормализуется: делится на Nominal.
        """
        target_codes = {"USD", "EUR", "CNY"}
        rates = {}
        root = ET.fromstring(xml_text)
        for valute in root.findall("Valute"):
            code = valute.find("CharCode").text
            if code in target_codes:
                nominal = int(valute.find("Nominal").text)
                value_str = valute.find("Value").text.replace(",", ".")
                rate = float(value_str) / nominal
                rates[code] = rate
        return rates

    def cache_db(self, rates):
        """
        Сохраняет курсы валют в БД.
        Если в БД уже есть запись за сегодня и её last_updated равен сегодняшней дате, то считаем данные свежими.
        Если запись существует, но не обновлялась сегодня, то обновляем её.
        Если записи за сегодня нет, создаём новую.
        """
        today_str = date.today().strftime("%d/%m/%Y")
        today = date.today()
        db = SessionLocal()
        # поиск записи по дате
        existing = db.query(CurrencyRates).filter(CurrencyRates.date == today_str).first()
        if existing:
            if existing.last_updated.date() != today:
                existing.usd = rates.get("USD")
                existing.eur = rates.get("EUR")
                existing.cny = rates.get("CNY")
                existing.last_updated = datetime.now()
        else:
            new_record = CurrencyRates(
                date=today_str, usd=rates.get("USD"), eur=rates.get("EUR"), cny=rates.get("CNY"), last_updated=datetime.now()
            )
            db.add(new_record)
        db.commit()
        db.close()

    def get_data_on_currency(self) -> dict:
        """
        Главный метод получения данных.

        – Запрашивает XML
        – Извлекает нужные курсы валют: USD, EUR, CNY
        – Сохраняет их в БД и возвращает словарь с курсами

        Возвращает данные в формате:
        {
        "USD": 100.01,
        "EUR": 123.34,
        "CNY": 12.4,
        }
        """
        xml_data = self.get_api_data()
        rates = self.parse_currency_data(xml_data)
        self.cache_db(rates)
        return rates


# print(Currency().get_data_on_currency())

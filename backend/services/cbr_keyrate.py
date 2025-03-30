# python -m services.cbr_keyrate
import requests
import xml.etree.ElementTree as ET
import json
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field
from typing import Dict, List, Literal
import logging
from sqlalchemy.orm import Session
from models.db_model import KeyRateTable, SessionLocal, PeriodEnum


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class KeyRate(BaseModel):
    periods: Dict[str, List[str]] = Field(default_factory=dict)
    period: Literal["D", "M6", "Y", "Y5", "Y10", "Y15"] = "D"

    def __init__(self, **data):
        super().__init__(**data)
        self.periods = self.generate_periods()

    def get_dates(self) -> List[str]:
        """
        Возвращает пару дат [to_date, from_date] (в формате YYYY-MM-DD)
        для выбранного периода.
        """
        return self.periods[self.period]

    def generate_periods(self) -> Dict[str, List[str]]:
        """
        Генерирует словарь периодов с датами для каждого периода.
        Ключи словаря соответствуют допустимым литералам: "D", "M", "Y", "Y5", "Y10".
        """
        today = date.today()
        periods = {
            "D": [today, today - relativedelta(days=7)],
            "M6": [today, today - relativedelta(months=6)],
            "Y": [today, today - relativedelta(years=1)],
            "Y5": [today, today - relativedelta(years=5)],
            "Y10": [today, today - relativedelta(years=10)],
            "Y15": [today, today - relativedelta(years=15)],
        }
        for key in periods.keys():
            pair = periods[key]
            periods[key] = [pair[0].strftime("%Y-%m-%d"), pair[1].strftime("%Y-%m-%d")]
        return periods

    def get_key_rate(self) -> dict:
        """
        Получает данные по ключевой ставке.
        Если для выбранного периода в БД есть свежие данные, они возвращаются;
        иначе данные запрашиваются через CBR API, сохраняются и возвращаются.
        """
        db: Session = SessionLocal()
        dates: List[str] = self.get_dates()
        from_date = dates[1]
        to_date = dates[0]

        recent_data = (
            db.query(KeyRateTable)
            .filter(
                KeyRateTable.period == PeriodEnum[self.period],
                KeyRateTable.date >= datetime.datetime.strptime(from_date, "%Y-%m-%d"),
            )
            .all()
        )
        if recent_data:
            data = [{"date": row.date, "rate": row.rate} for row in recent_data]
            if self.period == "D":
                data = data[0]
            db.close()
            return {"keyRate": data}

        logger.debug("Using CBR API: [from_date, to_date]: %s", self.periods[self.period])
        url = "https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"

        SOAPEnvelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <KeyRate xmlns="http://web.cbr.ru/">
      <fromDate>{from_date}</fromDate>
      <ToDate>{to_date}</ToDate>
    </KeyRate>
  </soap:Body>
</soap:Envelope>
"""
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://web.cbr.ru/KeyRate",
        }

        response = requests.post(url, data=SOAPEnvelope, headers=headers)
        data = []

        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
                namespaces = {
                    "soap": "http://schemas.xmlsoap.org/soap/envelope/",
                    "web": "http://web.cbr.ru/",
                    "diffgram": "urn:schemas-microsoft-com:xml-diffgram-v1",
                }

                key_rate_result = root.find(".//web:KeyRateResult", namespaces)
                if key_rate_result is None:
                    logger.error("Error: 'KeyRateResult' element not found.")
                    exit()

                diffgram = key_rate_result.find("diffgram:diffgram", namespaces)
                if diffgram is None:
                    logger.error("Error: 'diffgram' element not found.")
                    exit()

                key_rate = diffgram.find("KeyRate")
                if key_rate is None:
                    logger.error("Error: 'KeyRate' element not found.")
                    exit()

                for kr in key_rate.findall("KR"):
                    dt_str = kr.find("DT").text
                    rate = kr.find("Rate").text

                    dt_obj = datetime.datetime.fromisoformat(dt_str)
                    formatted_dt = int(dt_obj.timestamp())
                    data.append({"dt": formatted_dt, "rate": float(rate)})

                    db_row = KeyRateTable(
                        period=PeriodEnum[self.period],
                        date=dt_obj,
                        rate=float(rate),
                        last_updated=datetime.datetime.now(),
                    )
                    db.merge(db_row)
                db.commit()
                db.close()

                if self.period == "D":
                    data = data[0]

                logger.debug("Extracted Data in JSON Format: %s", data)
                return {"keyRate": data}

            except ET.ParseError as e:
                logger.error(f"XML Parse Error: {e}")
                raise e
        else:
            logger.error(f"Error: Received status code {response.status_code}")
            logger.debug("Response Text: %s", response.text)
            db.close()


# kr = KeyRate(period="M6").get_key_rate()
# print(kr)

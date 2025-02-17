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
    period: Literal["D", "M", "Y", "5Y", "10Y"] = "D"

    def __init__(self, **data):
        super().__init__(**data)
        self.periods = self.generate_periods()

    def get_dates(self) -> List[str]:
        return self.periods[self.period]

    def generate_periods(self) -> Dict[str, List[str]]:
        today = date.today()
        periods = {
            "D": [today, today - relativedelta(months=1)],
            "M": [today, today - relativedelta(months=1)],
            "Y": [today, today - relativedelta(years=1)],
            "5Y": [today, today - relativedelta(years=5)],
            "10Y": [today, today - relativedelta(years=10)],
        }  # current, month, year

        for key in periods.keys():
            if periods[key]:
                pair = periods[key]
                periods[key] = [pair[0].strftime("%Y-%m-%d"), pair[1].strftime("%Y-%m-%d")]

        return periods

    def get_key_rate(self) -> dict:
        db: Session = SessionLocal()
        dates: List[date, date] = self.get_dates()
        from_date = dates[1]
        to_date = dates[0]

        # check if data is recent (e.g., within the last day)
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

            return {"keyRate": data}

        logger.debug("Using CBR API: [from_date, to_date]: %s", self.periods[self.period])
        # source & docs : https://cbr.ru/DailyInfoWebServ/DailyInfo.asmx?op=KeyRate
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

        # headers, including the correct SOAPAction
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://web.cbr.ru/KeyRate",
        }

        response = requests.post(url, data=SOAPEnvelope, headers=headers)

        data = []

        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)

                # namespaces used in the XML
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

                # DEBUG: List all child elements within KeyRate to verify structure
                # print("Child elements within 'KeyRate':")
                # for child in key_rate:
                #     print(f"Tag: {child.tag}, Text: {child.text}")

                for kr in key_rate.findall("KR"):
                    dt_str = kr.find("DT").text
                    rate = kr.find("Rate").text

                    dt_obj = datetime.datetime.fromisoformat(dt_str)
                    # formatted_dt = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                    formatted_dt = int(dt_obj.timestamp())

                    data.append({"dt": formatted_dt, "rate": float(rate)})

                    # save to database
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

                # json_data = json.dumps(data, ensure_ascii=False, indent=4)
                logger.debug("Extracted Data in JSON Format: %s", data)
                return {"keyRate": data}

            except ET.ParseError as e:
                logger.error(f"XML Parse Error: {e}")
                raise e
        else:
            logger.error(f"Error: Received status code {response.status_code}")
            logger.debug("Response Text: %s", response.text)


kr = KeyRate(period="D").get_key_rate()

import pytest, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.db_model import Base, KeyRateTable, PeriodEnum
from ..services.cbr_keyrate import KeyRate
import requests

TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def override_session_local(monkeypatch):
    from ..services import cbr_keyrate

    monkeypatch.setattr(cbr_keyrate, "SessionLocal", TestingSessionLocal)


def dummy_post(url, data, headers):
    class DummyResponse:
        status_code = 200
        text = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <KeyRateResponse xmlns="http://web.cbr.ru/">
              <KeyRateResult>
                <diffgram:diffgram xmlns:diffgram="urn:schemas-microsoft-com:xml-diffgram-v1">
                  <KeyRate>
                    <KR>
                      <DT>{datetime.datetime.now().isoformat()}</DT>
                      <Rate>7.50</Rate>
                    </KR>
                  </KeyRate>
                </diffgram:diffgram>
              </KeyRateResult>
            </KeyRateResponse>
          </soap:Body>
        </soap:Envelope>"""

    return DummyResponse()


requests.post = dummy_post


@pytest.fixture
def key_rate():
    return KeyRate(period="D")


def test_get_key_rate(key_rate):
    session = TestingSessionLocal()
    dates = key_rate.get_dates()
    new_record = KeyRateTable(period=PeriodEnum["D"], date=datetime.datetime.now(), rate=7.5, last_updated=datetime.datetime.now())
    session.add(new_record)
    session.commit()
    session.close()
    result = key_rate.get_key_rate()
    assert "keyRate" in result
    if isinstance(result["keyRate"], dict):
        assert float(result["keyRate"]["rate"]) == 7.5

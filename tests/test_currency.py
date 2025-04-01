import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.db_model import Base, CurrencyRates
from ..services.cbr_currency import Currency

TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)
Currency.cache_db.__globals__["SessionLocal"] = TestingSessionLocal

import requests


def dummy_get(url):
    class DummyResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        @property
        def text(self):
            return """<?xml version="1.0" encoding="windows-1251"?>
            <ValCurs Date="01.01.2024" name="Foreign Currency Market">
                <Valute>
                    <CharCode>USD</CharCode>
                    <Nominal>1</Nominal>
                    <Value>75,00</Value>
                </Valute>
                <Valute>
                    <CharCode>EUR</CharCode>
                    <Nominal>1</Nominal>
                    <Value>85,00</Value>
                </Valute>
                <Valute>
                    <CharCode>CNY</CharCode>
                    <Nominal>10</Nominal>
                    <Value>110,00</Value>
                </Valute>
            </ValCurs>"""

    return DummyResponse()


requests.get = dummy_get


@pytest.fixture
def currency():
    return Currency()


def test_get_data_on_currency(currency):
    rates = currency.get_data_on_currency()
    assert rates["USD"] == 75.0
    assert rates["EUR"] == 85.0
    assert rates["CNY"] == 11.0  # 110/10

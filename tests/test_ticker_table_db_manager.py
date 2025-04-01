import pytest, json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.db_model import Base, TickerTable
from ..services.paper_data.ticker_table_db import TickerTableDBManager

TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)
TickerTableDBManager.get_session = lambda self: TestingSessionLocal()

from ..services.paper_data.paper_data import PaperData

dummy_table = {"uid": "dummy_uid", "figi": "dummy_figi", "ticker": "DUMMY"}
PaperData.get_uid_ticker_figi_data_by_ticker = lambda self, ticker: dummy_table


@pytest.fixture
def manager():
    return TickerTableDBManager()


def test_update_cache_and_getters(manager):
    data = manager.update_cache("TEST")
    loaded = json.loads(data) if isinstance(data, str) else data
    assert loaded["uid"] == "dummy_uid"
    uid = manager.get_uid_by_ticker("TEST")
    assert uid == "dummy_uid"
    figi = manager.get_figi_by_ticker("TEST")
    assert figi == "dummy_figi"


def test_get_ticker_by_uid(manager):
    _ = manager.update_cache("DUMMY")
    ticker = manager.get_ticker_by_uid("dummy_uid")
    assert ticker == "SBER"

import pytest, json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.db_model import Base, PaperDataCache
from ..services.paper_data.paper_data_db import PaperDataDBManager

TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)
PaperDataDBManager.get_session = lambda self: TestingSessionLocal()

from ..services.paper_data.paper_data import PaperData

dummy_paper = {"ticker": "DUMMY", "issue_size": 100, "year": [2020, 2021], "P/E": [10, 11], "year_change": [0.5, -0.2]}
PaperData.get_main_data_on_share_by_uid = lambda self, uid: dummy_paper
from ..services.paper_data.ticker_table_db import TickerTableDBManager

TickerTableDBManager.get_uid_by_ticker = lambda self, ticker: "dummy_uid"


@pytest.fixture
def manager():
    return PaperDataDBManager()


def test_update_and_get_cache(manager):
    assert manager.get_cache("TEST") is None
    data = manager.update_cache("TEST")
    assert data == dummy_paper
    assert manager.get_cache("TEST") == dummy_paper


def test_clear_outdated_cache(manager):
    _ = manager.update_cache("TEST")
    session = TestingSessionLocal()
    rec = session.query(PaperDataCache).filter(PaperDataCache.ticker == "TEST").first()
    rec.timestamp = datetime.now() - timedelta(days=100)
    session.commit()
    session.close()
    manager.clear_outdated_cache()
    assert manager.get_cache("TEST") is None

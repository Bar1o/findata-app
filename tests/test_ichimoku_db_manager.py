import sys
import types
from datetime import datetime, timedelta
import json
import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.db_model import Base, IchimokuIndexCache, SessionLocal
from ..services.ichimoku.ichimoku_db import IchimokuDbManager
import os

dummy_api = types.ModuleType("services.ichimoku.ichimoku_api")


class DummyIchimokuApi:
    def __init__(self, ticker, period):
        self.ticker = ticker
        self.period = period

    def get_all_candles_by_period(self):
        now_val = datetime.now()
        df = pd.DataFrame([{"time": now_val, "open": 100.0, "close": 110.0, "high": 115.0, "low": 95.0, "volume": 1000}])
        return df

    def export_nan(self, df):
        return {"tenkanSen": 100, "kijunSen": 105}


dummy_api.IchimokuApi = DummyIchimokuApi
sys.modules["services.ichimoku.ichimoku_api"] = dummy_api

TEST_ENGINE = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE)
SessionLocal.configure(bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def patch_ticker_table_db(monkeypatch):
    from services.paper_data.ticker_table_db import TickerTableDBManager

    monkeypatch.setattr(TickerTableDBManager, "update_cache", lambda self, ticker: json.dumps({"uid": "dummy", "figi": "dummy_figi"}))


@pytest.fixture(autouse=True)
def patch_ichimoku_api(monkeypatch):
    import services.ichimoku.ichimoku_api as ia

    monkeypatch.setattr(
        ia.IchimokuApi,
        "get_all_candles_by_period",
        lambda self: pd.DataFrame([{"time": datetime.now(), "open": 100.0, "close": 110.0, "high": 115.0, "low": 95.0, "volume": 1000}]),
    )
    monkeypatch.setattr(ia.IchimokuApi, "export_nan", lambda self, df: {"tenkanSen": 100, "kijunSen": 105})

    class DummyClient:
        def __init__(self, token):
            self.token = token

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def get_all_candles(self, **kwargs):
            return iter([])

    monkeypatch.setattr(ia, "Client", lambda token: DummyClient(token))


@pytest.fixture(scope="function", autouse=True)
def setup_db(monkeypatch):
    from ..services.ichimoku import ichimoku_db

    monkeypatch.setattr(ichimoku_db, "SessionLocal", TestingSessionLocal)
    Base.metadata.create_all(TEST_ENGINE)
    yield
    Base.metadata.drop_all(TEST_ENGINE)


@pytest.fixture
def manager():
    session = TestingSessionLocal()
    mgr = IchimokuDbManager(ticker="TEST", period="W")
    yield mgr
    session.close()


def test_update_and_get_cache(manager):
    assert manager.get_cache() is None
    manager.update_cache()
    cache = manager.get_cache()
    assert cache is not None
    assert json.loads(cache.data) == {"tenkanSen": 100, "kijunSen": 105}


def test_clear_outdated_cache(manager):
    manager.update_cache()
    session = TestingSessionLocal()
    rec = session.query(IchimokuIndexCache).filter_by(ticker="TEST", period="W").first()
    rec.timestamp = datetime.now() - timedelta(hours=2)
    session.commit()
    session.close()
    manager.clear_outdated_cache()
    assert manager.get_cache() is None

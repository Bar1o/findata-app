import json
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.db_model import Base, MultiplicatorsCache
from ..services.multiplicators.multiplicators_db import MultiplicatorsDBManager

engine = create_engine("sqlite:///:memory:")
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def override_session(monkeypatch):
    monkeypatch.setattr(MultiplicatorsDBManager, "get_session", lambda self: TestSessionLocal())
    yield


@pytest.fixture
def manager():
    return MultiplicatorsDBManager()


def test_save_cache_and_get_cache(manager):
    ticker = "TEST"
    data = {"value": 123}
    manager.save_cache(ticker, data)
    ret = manager.get_cache(ticker)
    assert ret == data


def test_get_cache_returns_none_for_outdated(manager):
    ticker = "OLD"
    data = {"value": 456}
    session = TestSessionLocal()
    past_time = datetime.now() - timedelta(days=100)
    cache_entry = MultiplicatorsCache(ticker=ticker, data=json.dumps(data), timestamp=past_time)
    session.add(cache_entry)
    session.commit()
    session.close()
    ret = manager.get_cache(ticker)
    assert ret is None


def test_clear_outdated_cache(manager):
    ticker = "REMOVE"
    data = {"value": 789}
    session = TestSessionLocal()
    past_time = datetime.now() - timedelta(days=100)
    cache_entry = MultiplicatorsCache(ticker=ticker, data=json.dumps(data), timestamp=past_time)
    session.add(cache_entry)
    session.commit()
    session.close()
    manager.clear_outdated_cache()
    session = TestSessionLocal()
    entry = session.query(MultiplicatorsCache).filter(MultiplicatorsCache.ticker == ticker).first()
    session.close()
    assert entry is None


def test_update_cache_uses_existing(manager):
    ticker = "EXIST"
    data = {"value": 111}
    manager.save_cache(ticker, data)
    ret = manager.update_cache(ticker)
    assert ret == data


def test_update_cache_fetches_new_data(manager, monkeypatch):
    ticker = "NEW"

    def fake_get_multiplicator_data_from_api(self):
        return {ticker: {"value": 222}}

    monkeypatch.setattr(
        "services.multiplicators.multiplicators.Multiplicators.get_multiplicator_data_from_api", fake_get_multiplicator_data_from_api
    )
    ret = manager.update_cache(ticker)
    assert ret == {"value": 222}
    cached = manager.get_cache(ticker)
    assert cached == {"value": 222}

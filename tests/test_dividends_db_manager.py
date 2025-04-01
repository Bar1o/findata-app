import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.db_model import Base, DividendsCache
from services.paper_data.ticker_table_db import TickerTableDBManager
from services.dividends.dividends_db import DividendsDBManager

MOCK_DIVIDEND_DATA = {"dividend_yield_daily_ttm": {"value": "10.50", "unit": "%"}, "payment_date": {"value": "2024-07-21", "unit": ""}}
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture
def test_db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def mock_dividends_manager(test_db_session):
    mock_ticker_db_manager = MagicMock(spec=TickerTableDBManager)
    mock_ticker_db_manager.get_figi_by_ticker.return_value = "dummy_figi"
    with patch("services.dividends.dividends_db.get_extended_dividend_data_by_ticker", return_value=MOCK_DIVIDEND_DATA), patch.object(
        DividendsDBManager, "get_session", return_value=test_db_session
    ):
        manager = DividendsDBManager()
        yield manager


def test_get_cache_empty(mock_dividends_manager, test_db_session):
    assert mock_dividends_manager.get_cache("NONEXISTENT") is None


def test_save_cache(mock_dividends_manager, test_db_session):
    ticker = "TEST_SAVE"
    data = {"test_key": "test_value"}
    existing = test_db_session.query(DividendsCache).filter(DividendsCache.ticker == ticker).first()
    if existing:
        test_db_session.delete(existing)
        test_db_session.commit()
    mock_dividends_manager.save_cache(ticker, data)
    cache_record = test_db_session.query(DividendsCache).filter(DividendsCache.ticker == ticker).first()
    assert cache_record is not None
    assert json.loads(cache_record.data) == data
    assert (datetime.now() - cache_record.timestamp).total_seconds() < 10


def test_update_cache_new(mock_dividends_manager):
    ticker = "TEST_NEW"
    expected_data = MOCK_DIVIDEND_DATA
    result = mock_dividends_manager.update_cache(ticker)
    assert result == expected_data
    cached = mock_dividends_manager.get_cache(ticker)
    assert cached == expected_data


def test_get_cache_fresh(mock_dividends_manager, test_db_session):
    ticker = "TEST_FRESH"
    data = {"fresh_data": "value"}
    existing = test_db_session.query(DividendsCache).filter(DividendsCache.ticker == ticker).first()
    if existing:
        test_db_session.delete(existing)
        test_db_session.commit()
    cache_record = DividendsCache(ticker=ticker, data=json.dumps(data), timestamp=datetime.now())
    test_db_session.add(cache_record)
    test_db_session.commit()
    result = mock_dividends_manager.get_cache(ticker)
    assert result == data


def test_clear_outdated_cache(mock_dividends_manager, test_db_session):
    fresh_ticker = "TEST_CLEAR_FRESH"
    outdated_ticker = "TEST_CLEAR_OUTDATED"
    for t in [fresh_ticker, outdated_ticker]:
        existing = test_db_session.query(DividendsCache).filter(DividendsCache.ticker == t).first()
        if existing:
            test_db_session.delete(existing)
    test_db_session.commit()
    fresh_data = {"fresh": "data"}
    outdated_data = {"old": "data"}
    fresh_cache = DividendsCache(ticker=fresh_ticker, data=json.dumps(fresh_data), timestamp=datetime.now())
    outdated_cache = DividendsCache(ticker=outdated_ticker, data=json.dumps(outdated_data), timestamp=datetime.now() - timedelta(days=100))
    test_db_session.add(fresh_cache)
    test_db_session.add(outdated_cache)
    test_db_session.commit()
    mock_dividends_manager.clear_outdated_cache()
    assert test_db_session.query(DividendsCache).filter(DividendsCache.ticker == fresh_ticker).first() is not None
    assert test_db_session.query(DividendsCache).filter(DividendsCache.ticker == outdated_ticker).first() is None

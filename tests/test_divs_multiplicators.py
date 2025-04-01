import json
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
from services.dividends.dividends import get_extended_dividend_data_by_ticker, get_dividend_data_by_ticker
from services.multiplicators.multiplicators import Multiplicators
from models.models import Quotation


@pytest.fixture
def mock_client():
    with patch("services.dividends.dividends.Client") as mock:
        client_instance = Mock()
        mock.return_value.__enter__.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_db_manager():
    with patch("services.dividends.dividends.db_manager") as mock:
        mock.get_figi_by_ticker.return_value = "BBG000BVPV84"
        yield mock


@pytest.fixture
def mock_multiplicators():
    with patch("services.dividends.dividends.Multiplicators") as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        mock_instance.get_divs_from_multiplicator_data_from_api.return_value = {
            "dividend_yield_daily_ttm": {"value": "10.49", "unit": "%"},
            "five_years_average_dividend_yield": {"value": "8.75", "unit": "%"},
        }
        yield mock_instance


@pytest.fixture
def mock_dividend_response():
    dividend_mock = MagicMock()
    dividend_mock.dividend_net = Quotation(units=10, nano=500000000)
    dividend_mock.payment_date = datetime.now() + timedelta(days=30)
    dividend_mock.declared_date = datetime.now() - timedelta(days=10)
    dividend_mock.last_buy_date = datetime.now() + timedelta(days=15)
    dividend_mock.dividend_type = "DIVIDEND_TYPE_ORDINARY"
    dividend_mock.record_date = datetime.now() + timedelta(days=20)
    dividend_mock.regularity = "DIVIDEND_REGULARITY_ANNUAL"
    dividend_mock.close_price = Quotation(units=150, nano=0)
    dividend_mock.yield_value = Quotation(units=7, nano=0)
    dividend_mock.created_at = datetime.now() - timedelta(days=5)
    response_mock = MagicMock()
    response_mock.dividends = [dividend_mock]
    return response_mock


def test_get_dividend_data_by_ticker(mock_client, mock_db_manager, mock_dividend_response):
    mock_client.instruments.get_dividends.return_value = mock_dividend_response
    result = get_dividend_data_by_ticker("SBER")
    mock_db_manager.get_figi_by_ticker.assert_called_once_with("SBER")
    mock_client.instruments.get_dividends.assert_called_once()
    assert isinstance(result, dict)
    assert "dividend_net" in result
    assert "payment_date" in result
    assert "yield_value" in result
    assert float(result["dividend_net"]) == 10.5


def test_get_extended_dividend_data_by_ticker(mock_client, mock_db_manager, mock_dividend_response, mock_multiplicators):
    with patch("services.dividends.dividends.get_dividend_data_by_ticker") as mock_get_div:
        mock_get_div.return_value = {
            "dividend_net": "10.5",
            "payment_date": datetime.now() + timedelta(days=30),
            "yield_value": "7.0",
            "close_price": "150.0",
            "declared_date": datetime.now() - timedelta(days=10),
            "last_buy_date": datetime.now() + timedelta(days=15),
            "record_date": datetime.now() + timedelta(days=20),
            "dividend_type": "DIVIDEND_TYPE_ORDINARY",
            "regularity": "DIVIDEND_REGULARITY_ANNUAL",
            "created_at": datetime.now() - timedelta(days=5),
        }
        result = get_extended_dividend_data_by_ticker("SBER")
        mock_get_div.assert_called_once_with("SBER")
        mock_multiplicators.get_divs_from_multiplicator_data_from_api.assert_called_once_with("SBER")
        assert isinstance(result, dict)
        assert "dividend_net" in result
        assert result["dividend_net"]["value"] == "10.50"
        assert result["dividend_net"]["unit"] == "руб"
        assert "dividend_yield_daily_ttm" in result
        assert result["dividend_yield_daily_ttm"]["value"] == "10.49"


@pytest.fixture
def mock_multiplicator_client():
    with patch("services.multiplicators.multiplicators.Client") as mock:
        client_instance = Mock()
        mock.return_value.__enter__.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_multiplicator_db():
    return MagicMock(get_uid_by_ticker=Mock(return_value="BBG000BVPV84"))


def test_get_divs_from_multiplicator_data_from_api(mock_multiplicator_client, mock_multiplicator_db):
    response_mock = MagicMock()
    fundamental_mock = MagicMock()
    fundamental_mock.current_ratio_mrq = 1.2
    fundamental_mock.five_years_average_dividend_yield = 8.75
    fundamental_mock.dividend_payout_ratio_fy = 50.0
    fundamental_mock.forward_annual_dividend_yield = 9.5
    response_mock.fundamentals = [fundamental_mock]
    mock_multiplicator_client.instruments.get_asset_fundamentals.return_value = response_mock
    multiplicator = Multiplicators()
    multiplicator.token = "test_token"
    multiplicator.db_manager = mock_multiplicator_db
    result = multiplicator.get_divs_from_multiplicator_data_from_api("SBER")
    mock_multiplicator_db.get_uid_by_ticker.assert_called_once_with("SBER")
    assert isinstance(result, dict)
    assert "five_years_average_dividend_yield" in result
    assert isinstance(result["five_years_average_dividend_yield"], dict)
    assert result["five_years_average_dividend_yield"]["value"] == "8.75"
    assert result["five_years_average_dividend_yield"]["unit"] == "%"

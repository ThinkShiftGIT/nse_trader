"""Unit tests for the data fetcher module."""
import pytest
import json
from unittest.mock import MagicMock, patch
from nse_trader.data_fetcher import NSEDataFetcher

@pytest.fixture
def mock_yfinance(mocker):
    """Mock the yfinance library."""
    return mocker.patch('nse_trader.data_fetcher.yf.Ticker')

def test_load_stocks():
    """Test loading stocks from a JSON file."""
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = '[{"symbol": "MTNN"}]'
        fetcher = NSEDataFetcher()
        assert fetcher.get_stock_list() == [{'symbol': 'MTNN'}]

def test_load_stocks_file_not_found():
    """Test handling of FileNotFoundError when loading stocks."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        fetcher = NSEDataFetcher()
        assert fetcher.get_stock_list() == []

def test_get_stock_data(mock_yfinance):
    """Test getting data for a single stock."""
    mock_ticker = MagicMock()
    mock_ticker.info = {'symbol': 'MTNN', 'currentPrice': 100.0, 'previousClose': 95.0, 'volume': 1000, 'marketCap': 1000000, 'dayHigh': 101.0, 'dayLow': 99.0, 'open': 99.5, 'longName': 'MTN Nigeria'}
    mock_yfinance.return_value = mock_ticker

    fetcher = NSEDataFetcher(stocks_file='dummy.json')
    data = fetcher.get_stock_data('MTNN')

    assert data is not None
    assert data['symbol'] == 'MTNN'
    assert data['price_raw'] == 100.0

def test_get_market_summary(mock_yfinance):
    """Test getting market summary."""
    mock_ticker = MagicMock()
    mock_ticker.info = {'symbol': '^NGSEASI', 'currentPrice': 1234.56, 'previousClose': 1230.0, 'volume': 5000}
    mock_yfinance.return_value = mock_ticker

    fetcher = NSEDataFetcher(stocks_file='dummy.json')
    summary = fetcher.get_market_summary()

    assert summary is not None
    assert summary['asi_raw'] == 1234.56

def test_get_historical_data(mock_yfinance):
    """Test getting historical data."""
    mock_history = MagicMock()
    mock_history.empty = False
    mock_history.reset_index.return_value = mock_history
    mock_history.to_dict.return_value = [{'date': '2023-01-01', 'close': 100.0}]

    mock_ticker = MagicMock()
    mock_ticker.history.return_value = mock_history
    mock_yfinance.return_value = mock_ticker

    fetcher = NSEDataFetcher(stocks_file='dummy.json')
    history = fetcher.get_historical_data('MTNN')

    assert history is not None
    assert len(history) == 1
    assert history[0]['close'] == 100.0

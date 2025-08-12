"""Unit tests for the Flask application."""
import pytest
from unittest.mock import MagicMock
from nse_trader.app import create_app

@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_data_fetcher(mocker):
    """Mock the NSEDataFetcher class."""
    mock = MagicMock()
    mocker.patch('nse_trader.app.NSEDataFetcher', return_value=mock)
    return mock

@pytest.fixture
def mock_analyzer(mocker):
    """Mock the TechnicalAnalyzer class."""
    mock = MagicMock()
    mocker.patch('nse_trader.app.TechnicalAnalyzer', return_value=mock)
    return mock

def test_market_summary_api(client, mock_data_fetcher):
    """Test the /api/market-summary endpoint."""
    mock_data_fetcher.get_market_summary.return_value = {'asi': '1234.56'}
    response = client.get('/api/market-summary')
    assert response.status_code == 200
    assert response.json == {'asi': '1234.56'}

    mock_data_fetcher.get_market_summary.return_value = {}
    response = client.get('/api/market-summary')
    assert response.status_code == 500
    assert 'error' in response.json

def test_get_stock_api(client, mock_data_fetcher):
    """Test the /api/stock/<symbol> endpoint."""
    mock_data_fetcher.get_stock_data.return_value = {'symbol': 'MTNN', 'price': 100.0}
    response = client.get('/api/stock/MTNN')
    assert response.status_code == 200
    assert response.json == {'symbol': 'MTNN', 'price': 100.0}

    mock_data_fetcher.get_stock_data.return_value = None
    response = client.get('/api/stock/UNKNOWN')
    assert response.status_code == 404
    assert 'error' in response.json

def test_get_historical_api(client, mock_data_fetcher):
    """Test the /api/historical/<symbol> endpoint."""
    mock_data_fetcher.get_historical_data.return_value = [{'date': '2023-01-01', 'close': 100.0}]
    response = client.get('/api/historical/MTNN')
    assert response.status_code == 200
    assert response.json == [{'date': '2023-01-01', 'close': 100.0}]

    mock_data_fetcher.get_historical_data.return_value = []
    response = client.get('/api/historical/UNKNOWN')
    assert response.status_code == 404
    assert 'error' in response.json

def test_get_stock_list_api(client, mock_data_fetcher):
    """Test the /api/stocks/list endpoint."""
    mock_data_fetcher.get_stock_list.return_value = [{'symbol': 'MTNN', 'name': 'MTN Nigeria'}]
    response = client.get('/api/stocks/list')
    assert response.status_code == 200
    assert response.json == [{'symbol': 'MTNN', 'name': 'MTN Nigeria'}]

def test_get_analysis_api(client, mock_data_fetcher, mock_analyzer):
    """Test the /api/analysis/<symbol> endpoint."""
    mock_data_fetcher.get_historical_data.return_value = [{'date': '2023-01-01', 'close': 100.0}]
    mock_analyzer.analyze_stock.return_value = {'recommendation': 'buy'}
    mock_analyzer.calculate_entry_exit_points.return_value = {'stop_loss': 95.0}

    response = client.get('/api/analysis/MTNN')

    assert response.status_code == 200
    assert response.json['recommendation'] == 'buy'
    assert response.json['stop_loss'] == 95.0

    mock_data_fetcher.get_historical_data.return_value = []
    response = client.get('/api/analysis/UNKNOWN')
    assert response.status_code == 404
    assert 'error' in response.json

"""Unit tests for NSE scraper module."""
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from nse_trader.scraper import NSEScraper

@pytest.fixture
def mock_response():
    """Create a mock response with sample HTML."""
    html = """
    <html>
        <div>ASI<div>40000.00</div></div>
        <div>Market Cap<div>₦20,000,000.00</div></div>
        <div>Volume<div>100,000,000</div></div>
        <div>Value<div>₦500,000.00</div></div>
        <div>Deals<div>1,000</div></div>
        <table>
            <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Price</th>
                <th>Change</th>
                <th>Volume</th>
            </tr>
            <tr>
                <td>DANGCEM</td>
                <td>Dangote Cement</td>
                <td>₦240.00</td>
                <td>2.50</td>
                <td>1,000,000</td>
            </tr>
        </table>
    </html>
    """
    return Mock(text=html, status_code=200)

@pytest.fixture
def scraper():
    """Create NSEScraper instance."""
    return NSEScraper()

def test_parse_float():
    """Test float parsing from NSE number format."""
    scraper = NSEScraper()
    
    assert scraper._parse_float('₦1,234.56') == 1234.56
    assert scraper._parse_float('1,234.56') == 1234.56
    assert scraper._parse_float('₦1,234') == 1234.0
    assert scraper._parse_float('invalid') == 0.0
    assert scraper._parse_float('') == 0.0

def test_parse_int():
    """Test integer parsing from NSE number format."""
    scraper = NSEScraper()
    
    assert scraper._parse_int('1,234') == 1234
    assert scraper._parse_int('1234') == 1234
    assert scraper._parse_int('invalid') == 0
    assert scraper._parse_int('') == 0

@patch('requests.Session.get')
def test_get_market_summary(mock_get, scraper, mock_response):
    """Test market summary scraping."""
    mock_get.return_value = mock_response
    
    summary = scraper.get_market_summary()
    
    assert summary['asi'] == 40000.0
    assert summary['market_cap'] == 20000000.0
    assert summary['volume'] == 100000000
    assert summary['value'] == 500000.0
    assert summary['deals'] == 1000

@patch('requests.Session.get')
def test_get_stock_price(mock_get, scraper, mock_response):
    """Test stock price scraping."""
    mock_get.return_value = mock_response
    
    price_data = scraper.get_stock_price('DANGCEM')
    
    assert price_data is not None
    assert price_data['symbol'] == 'DANGCEM'

@patch('requests.Session.get')
def test_scrape_stock_list(mock_get, scraper, mock_response):
    """Test stock list scraping."""
    mock_get.return_value = mock_response
    
    stocks = scraper._scrape_stock_list('mock_url')
    
    assert len(stocks) == 1
    assert stocks[0]['symbol'] == 'DANGCEM'
    assert stocks[0]['name'] == 'Dangote Cement'
    assert stocks[0]['price'] == 240.0
    assert stocks[0]['change'] == 2.5
    assert stocks[0]['volume'] == 1000000

@patch('requests.Session.get')
def test_error_handling(mock_get, scraper):
    """Test error handling in scraper."""
    # Simulate network error
    mock_get.side_effect = Exception('Network error')
    
    summary = scraper.get_market_summary()
    assert summary == {}
    
    price_data = scraper.get_stock_price('DANGCEM')
    assert price_data is None
    
    stocks = scraper.get_top_gainers()
    assert stocks == []

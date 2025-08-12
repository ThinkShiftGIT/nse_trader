"""Data fetching module for NSE stock data using yfinance."""
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import yfinance as yf
from nse_trader.utils import format_currency, format_number

logger = logging.getLogger(__name__)

class NSEDataFetcher:
    """Handles fetching and processing of NSE stock data from Yahoo Finance."""

    def __init__(self, stocks_file='stocks.json'):
        self.logger = logging.getLogger(__name__)
        self.stocks = self._load_stocks(stocks_file)

    def _load_stocks(self, stocks_file: str) -> List[Dict]:
        """Load stock list from a JSON file."""
        try:
            with open(stocks_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Stocks file not found: {stocks_file}")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding JSON from {stocks_file}")
            return []

    def get_stock_list(self) -> List[Dict]:
        """Return a list of available stocks."""
        return self.stocks

    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get data for a single stock."""
        try:
            # Append .NS for Nigerian stocks for yfinance
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info

            if not info or 'symbol' not in info:
                self.logger.warning(f"No data found for symbol: {symbol}")
                return None

            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            previous_close = info.get('previousClose', 0)
            change = price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': format_currency(price),
                'price_raw': price,
                'change': change,
                'change_percent': f"{change_percent:.2f}%",
                'volume': format_number(info.get('volume', 0)),
                'volume_raw': info.get('volume', 0),
                'market_cap': format_currency(info.get('marketCap', 0)),
                'market_cap_raw': info.get('marketCap', 0),
                'high': format_currency(info.get('dayHigh', 0)),
                'low': format_currency(info.get('dayLow', 0)),
                'open': format_currency(info.get('open', 0)),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return stock_data
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def get_market_summary(self) -> Dict:
        """Get NSE market summary using the NGX All-Share Index (^NGSEASI)."""
        try:
            ticker = yf.Ticker("^NGSEASI")
            info = ticker.info

            if not info:
                return {}

            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            previous_close = info.get('previousClose', 0)
            change = price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0

            return {
                'asi': format_number(price, 2),
                'asi_raw': price,
                'change': change,
                'change_percent': f"{change_percent:.2f}%",
                'volume': format_number(info.get('volume', 0)),
                'volume_raw': info.get('volume', 0),
                'value': format_currency(info.get('volume', 0) * price),
                'value_raw': info.get('volume', 0) * price,
                'market_cap': 'N/A', # Market cap for index is not directly available
                'market_cap_raw': 0,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.logger.error(f"Error fetching market summary: {str(e)}")
            return {}

    def get_historical_data(self, symbol: str, period: str = '1y', interval: str = '1d') -> List[Dict]:
        """Fetch historical data for a given stock symbol."""
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            history = ticker.history(period=period, interval=interval)

            if history.empty:
                return []

            history = history.reset_index()
            history.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
            return history.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return []

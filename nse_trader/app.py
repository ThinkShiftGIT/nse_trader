"""Main application module for NSE Trader."""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import logging

from .config import Config
from .data_fetcher import NSEDataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    
    # Initialize data fetcher
    data_fetcher = NSEDataFetcher()

    @app.route('/')
    def index():
        """Render the main page."""
        return render_template('index.html')

    @app.route('/api/market-summary')
    def get_market_summary():
        """Get NSE market summary."""
        try:
            summary = data_fetcher.get_market_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return jsonify({'error': 'Failed to fetch market summary'}), 500
    
    @app.route('/api/stocks/top')
    def get_top_stocks():
        """Get list of top stocks with analysis."""
        try:
            stocks = data_fetcher.get_top_stocks(limit=10)
            return jsonify(stocks)
        except Exception as e:
            logger.error(f"Error getting stocks: {str(e)}")
            return jsonify({'error': 'Failed to fetch stocks'}), 500
    
    @app.route('/api/stock/<symbol>')
    def get_stock(symbol):
        """Get detailed information for a specific stock."""
        try:
            quote = data_fetcher.get_delayed_quote(symbol)
            if not quote:
                return jsonify({'error': f'Stock {symbol} not found'}), 404
            return jsonify(quote)
        except Exception as e:
            logger.error(f"Error getting stock {symbol}: {str(e)}")
            return jsonify({'error': f'Failed to fetch stock {symbol}'}), 500

    @app.route('/api/historical/<symbol>')
    def get_historical(symbol):
        """Get historical data for a specific stock."""
        try:
            data = data_fetcher.get_historical_data(symbol)
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return jsonify({'error': f'Failed to fetch historical data for {symbol}'}), 500

    @app.route('/api/stocks/list')
    def get_stock_list():
        """Get a list of available stocks."""
        try:
            stocks = data_fetcher.get_stock_list()
            return jsonify(stocks)
        except Exception as e:
            logger.error(f"Error getting stock list: {str(e)}")
            return jsonify({'error': 'Failed to fetch stock list'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

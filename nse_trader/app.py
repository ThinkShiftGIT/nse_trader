"""Main application module for NSE Trader."""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import logging

from .config import Config
from .data_fetcher import NSEDataFetcher
from .technical_analysis import TechnicalAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)

    @app.route('/')
    def index():
        """Render the main page."""
        return render_template('index.html')

    @app.route('/api/market-summary')
    def market_summary():
        """Get NSE market summary data."""
        try:
            data_fetcher = NSEDataFetcher()
            summary = data_fetcher.get_market_summary()
            if not summary:
                return jsonify({'error': 'Failed to fetch market summary'}), 500
            return jsonify(summary)
        except Exception as e:
            app.logger.error(f"Error fetching market summary: {str(e)}")
            return jsonify({'error': 'An unexpected error occurred'}), 500

    @app.route('/api/stock/<symbol>')
    def get_stock(symbol):
        """Get detailed information for a specific stock."""
        try:
            data_fetcher = NSEDataFetcher()
            stock_data = data_fetcher.get_stock_data(symbol)
            if not stock_data:
                return jsonify({'error': f'Stock {symbol} not found'}), 404
            return jsonify(stock_data)
        except Exception as e:
            logger.error(f"Error getting stock {symbol}: {str(e)}")
            return jsonify({'error': f'Failed to fetch stock {symbol}'}), 500

    @app.route('/api/historical/<symbol>')
    def get_historical(symbol):
        """Get historical data for a specific stock."""
        try:
            data_fetcher = NSEDataFetcher()
            data = data_fetcher.get_historical_data(symbol)
            if not data:
                return jsonify({'error': f'No historical data found for {symbol}'}), 404
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return jsonify({'error': f'Failed to fetch historical data for {symbol}'}), 500

    @app.route('/api/stocks/list')
    def get_stock_list():
        """Get a list of available stocks."""
        try:
            data_fetcher = NSEDataFetcher()
            stocks = data_fetcher.get_stock_list()
            return jsonify(stocks)
        except Exception as e:
            logger.error(f"Error getting stock list: {str(e)}")
            return jsonify({'error': 'Failed to fetch stock list'}), 500
            
    @app.route('/api/analysis/<symbol>')
    def get_analysis(symbol):
        """Get technical analysis for a specific stock."""
        try:
            data_fetcher = NSEDataFetcher()
            analyzer = TechnicalAnalyzer()
            historical_data = data_fetcher.get_historical_data(symbol)
            if not historical_data:
                return jsonify({'error': f'No historical data found for {symbol}'}), 404
            
            prices = [d['close'] for d in historical_data]
            analysis = analyzer.analyze_stock(prices)
            
            # Add entry/exit points to the analysis
            entry_exit_points = analyzer.calculate_entry_exit_points(prices)
            analysis.update(entry_exit_points)

            return jsonify(analysis)
        except Exception as e:
            logger.error(f"Error getting analysis for {symbol}: {str(e)}")
            return jsonify({'error': f'Failed to get analysis for {symbol}'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

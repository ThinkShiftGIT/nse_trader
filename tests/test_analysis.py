"""Unit tests for technical analysis module."""
import pytest
import numpy as np
import pandas as pd
import pandas_ta as ta
from nse_trader.technical_analysis import TechnicalAnalyzer

@pytest.fixture
def sample_prices():
    """Create sample price data (list of floats) for testing."""
    np.random.seed(42)
    prices = (np.random.randn(100).cumsum() + 100).tolist() 
    return prices

@pytest.fixture
def short_prices():
    """Create short price data (list of floats) for testing default/edge cases."""
    np.random.seed(42)
    prices = (np.random.randn(40).cumsum() + 100).tolist()
    return prices

@pytest.fixture
def very_short_prices():
    """Create very short price data for edge case testing."""
    return [100, 101, 102]

def test_analyze_stock_structure_and_values(sample_prices):
    """Test technical analysis calculations and structure from analyze_stock."""
    analyzer = TechnicalAnalyzer()
    analysis = analyzer.analyze_stock(sample_prices) 
    
    assert 'recommendation' in analysis
    assert 'confidence' in analysis
    assert 'indicators' in analysis
    
    indicators = analysis['indicators']
    assert 'rsi' in indicators
    assert 'macd' in indicators
    assert 'bollinger' in indicators
    assert 'momentum' in indicators
    
    assert 0 <= indicators['rsi'] <= 100
    assert analysis['recommendation'] in ['buy', 'sell', 'neutral']
    assert analysis['confidence'] in ['low', 'medium', 'high']
    assert indicators['macd'] in ['buy', 'sell', 'neutral']
    assert indicators['bollinger'] in ['buy', 'sell', 'neutral']
    assert isinstance(indicators['momentum'], float)

def test_empty_data_handling(very_short_prices):
    """Test handling of insufficient data."""
    analyzer = TechnicalAnalyzer()
    
    analysis = analyzer.analyze_stock(very_short_prices)
    
    assert analysis['recommendation'] == 'neutral'
    assert analysis['confidence'] == 'low'

    analysis_empty = analyzer.analyze_stock([])
    assert analysis_empty['recommendation'] == 'neutral'
    assert analysis_empty['confidence'] == 'low'

def test_calculate_rsi(sample_prices):
    analyzer = TechnicalAnalyzer()
    rsi = analyzer.calculate_rsi(sample_prices)
    assert 0 <= rsi <= 100

def test_calculate_macd(sample_prices):
    analyzer = TechnicalAnalyzer()
    macd_data = analyzer.calculate_macd(sample_prices)
    assert 'macd_line' in macd_data
    assert 'signal_line' in macd_data
    assert 'histogram' in macd_data
    assert macd_data['signal'] in ['buy', 'sell', 'neutral']

def test_calculate_bollinger_bands(sample_prices):
    analyzer = TechnicalAnalyzer()
    bb_data = analyzer.calculate_bollinger_bands(sample_prices)
    assert 'upper_band' in bb_data
    assert 'middle_band' in bb_data
    assert 'lower_band' in bb_data
    assert bb_data['signal'] in ['buy', 'sell', 'neutral']
    if bb_data['middle_band'] != 0:
      assert bb_data['lower_band'] <= bb_data['middle_band'] <= bb_data['upper_band']

def test_calculate_momentum(sample_prices):
    analyzer = TechnicalAnalyzer()
    momentum = analyzer.calculate_momentum(sample_prices)
    assert isinstance(momentum, float)

@pytest.fixture
def fixed_prices():
    """Create a fixed set of price data for correctness testing."""
    return [
        100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
        109, 108, 107, 106, 105, 104, 103, 102, 101, 100,
        101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
        111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
    ]

def test_indicator_correctness(fixed_prices):
    """Test the correctness of technical indicators against a reference implementation."""
    analyzer = TechnicalAnalyzer()
    prices_series = pd.Series(fixed_prices)

    # RSI
    expected_rsi = ta.rsi(prices_series, length=14).iloc[-1]
    actual_rsi = analyzer.calculate_rsi(fixed_prices)
    assert np.isclose(actual_rsi, expected_rsi)

    # MACD
    macd_df = ta.macd(prices_series, fast=12, slow=26, signal=9)
    expected_macd_line = macd_df['MACD_12_26_9'].iloc[-1]
    expected_signal_line = macd_df['MACDs_12_26_9'].iloc[-1]
    actual_macd = analyzer.calculate_macd(fixed_prices)
    assert np.isclose(actual_macd['macd_line'], expected_macd_line, rtol=1e-2)
    assert np.isclose(actual_macd['signal_line'], expected_signal_line, rtol=1e-2)

    # Bollinger Bands
    bb_df = ta.bbands(prices_series, length=20, std=2, ddof=0)
    expected_upper_band = bb_df['BBU_20_2.0'].iloc[-1]
    expected_middle_band = bb_df['BBM_20_2.0'].iloc[-1]
    expected_lower_band = bb_df['BBL_20_2.0'].iloc[-1]
    actual_bb = analyzer.calculate_bollinger_bands(fixed_prices)
    assert np.isclose(actual_bb['upper_band'], expected_upper_band)
    assert np.isclose(actual_bb['middle_band'], expected_middle_band)
    assert np.isclose(actual_bb['lower_band'], expected_lower_band)

def test_calculate_entry_exit_points(fixed_prices):
    """Test the calculation of entry and exit points."""
    analyzer = TechnicalAnalyzer()
    points = analyzer.calculate_entry_exit_points(fixed_prices)
    assert 'price' in points
    assert 'stop_loss' in points
    assert 'take_profit' in points
    assert points['price'] == fixed_prices[-1]

    current_price = fixed_prices[-1]
    volatility_factor = 0.05
    if current_price > 1000:
        volatility_factor = 0.03
    elif current_price > 500:
        volatility_factor = 0.04
    elif current_price < 50:
        volatility_factor = 0.08

    expected_stop_loss = round(current_price * (1 - volatility_factor), 2)
    expected_take_profit = round(current_price * (1 + (volatility_factor * 1.5)), 2)
    assert points['stop_loss'] == expected_stop_loss
    assert points['take_profit'] == expected_take_profit

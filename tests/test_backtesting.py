"""Unit tests for backtesting module."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from nse_trader.backtesting import Backtester, Position, BacktestResult

@pytest.fixture
def sample_data():
    """Create sample price data for testing."""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    n = len(dates)
    
    # Generate synthetic price data with a trend
    np.random.seed(42)
    trend = np.linspace(0, 2, n)  # Upward trend
    noise = np.random.randn(n) * 0.1
    prices = 100 * (1 + trend + noise)  # Start at 100 with trend and noise
    
    df = pd.DataFrame({
        'Open': prices + np.random.randn(n) * 0.1,
        'High': prices + np.random.randn(n) * 0.2,
        'Low': prices - np.random.randn(n) * 0.2,
        'Close': prices,
        'Volume': np.random.randint(1000, 100000, n)
    }, index=dates)
    
    return df

def test_position():
    """Test Position class functionality."""
    # Test long position
    pos = Position('STOCK', 100.0, datetime.now(), 100, 'long')
    pos.close(110.0, datetime.now())
    
    assert pos.pnl == 1000.0  # (110 - 100) * 100
    assert pos.return_pct == 10.0
    
    # Test short position
    pos = Position('STOCK', 100.0, datetime.now(), 100, 'short')
    pos.close(90.0, datetime.now())
    
    assert pos.pnl == 1000.0  # (100 - 90) * 100
    assert pos.return_pct == 10.0

def test_backtest_result():
    """Test BacktestResult metrics calculation."""
    result = BacktestResult()
    
    # Add some sample positions
    positions = [
        Position('STOCK', 100.0, datetime(2024, 1, 1), 100, 'long'),
        Position('STOCK', 110.0, datetime(2024, 2, 1), 100, 'long'),
        Position('STOCK', 120.0, datetime(2024, 3, 1), 100, 'long')
    ]
    
    # Close positions with profits and losses
    positions[0].close(110.0, datetime(2024, 1, 15))  # Profit
    positions[1].close(105.0, datetime(2024, 2, 15))  # Loss
    positions[2].close(130.0, datetime(2024, 3, 15))  # Profit
    
    result.positions = positions
    result.equity_curve = pd.Series([100000, 101000, 100500, 101500],
                                  index=pd.date_range(start='2024-01-01', 
                                                    end='2024-03-15', 
                                                    freq='M'))
    
    result.calculate_metrics()
    
    assert result.total_trades == 3
    assert result.win_rate == pytest.approx(66.67, 0.01)
    assert result.profit_factor > 1.0

def test_sma_crossover_strategy(sample_data):
    """Test SMA crossover strategy."""
    backtester = Backtester(initial_capital=100000.0)
    strategy = backtester.create_sma_crossover_strategy(fast_period=50, 
                                                      slow_period=200)
    
    result = backtester.run(sample_data, strategy)
    
    assert isinstance(result, BacktestResult)
    assert result.total_trades > 0
    assert result.equity_curve is not None
    assert len(result.equity_curve) > 0

def test_rsi_strategy(sample_data):
    """Test RSI strategy."""
    backtester = Backtester(initial_capital=100000.0)
    strategy = backtester.create_rsi_strategy(oversold=30, overbought=70)
    
    result = backtester.run(sample_data, strategy)
    
    assert isinstance(result, BacktestResult)
    assert result.total_trades > 0
    assert result.equity_curve is not None
    assert len(result.equity_curve) > 0

def test_empty_data():
    """Test backtesting with empty data."""
    backtester = Backtester()
    strategy = backtester.create_sma_crossover_strategy()
    
    empty_df = pd.DataFrame()
    result = backtester.run(empty_df, strategy)
    
    assert isinstance(result, BacktestResult)
    assert result.total_trades == 0
    assert result.total_return == 0.0

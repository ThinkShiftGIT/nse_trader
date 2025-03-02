"""
Technical analysis module for NSE Trader application.
Contains various indicators and strategies for stock analysis.
"""

import numpy as np

class TechnicalAnalyzer:
    """
    Provides technical analysis indicators and trading signals.
    """
    
    def __init__(self):
        """Initialize the technical analyzer"""
        pass
        
    def calculate_rsi(self, prices, period=14):
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices (list): List of closing prices
            period (int): RSI period, default is 14
            
        Returns:
            float: RSI value from 0-100
        """
        if len(prices) < period + 1:
            return 50  # Default neutral value
            
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Create arrays of gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if len(deltas) > period:
            # Calculate smoothed average for gains and losses
            for i in range(period, len(deltas)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        # Calculate RS
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """
        Calculate Moving Average Convergence Divergence (MACD)
        
        Args:
            prices (list): List of closing prices
            fast (int): Fast EMA period
            slow (int): Slow EMA period
            signal (int): Signal EMA period
            
        Returns:
            dict: Dictionary with macd_line, signal_line, and histogram values
        """
        if len(prices) < slow + signal:
            return {
                'macd_line': 0,
                'signal_line': 0,
                'histogram': 0,
                'signal': 'neutral'
            }
            
        # Calculate fast EMA
        ema_fast = self._calculate_ema(prices, fast)
        
        # Calculate slow EMA
        ema_slow = self._calculate_ema(prices, slow)
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = self._calculate_ema(macd_line, signal)
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        # Determine signal
        signal_type = 'neutral'
        if macd_line > signal_line:
            signal_type = 'buy'
        elif macd_line < signal_line:
            signal_type = 'sell'
            
        return {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram,
            'signal': signal_type
        }
        
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """
        Calculate Bollinger Bands
        
        Args:
            prices (list): List of closing prices
            period (int): Period for SMA
            std_dev (int): Number of standard deviations
            
        Returns:
            dict: Dictionary with upper_band, middle_band, lower_band, and band_width
        """
        if len(prices) < period:
            return {
                'upper_band': prices[-1] * 1.1,
                'middle_band': prices[-1],
                'lower_band': prices[-1] * 0.9,
                'band_width': 0.2,
                'signal': 'neutral'
            }
            
        # Calculate middle band (SMA)
        middle_band = sum(prices[-period:]) / period
        
        # Calculate standard deviation
        std = np.std(prices[-period:])
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        # Calculate band width
        band_width = (upper_band - lower_band) / middle_band
        
        # Determine signal
        signal_type = 'neutral'
        current_price = prices[-1]
        
        if current_price > upper_band:
            signal_type = 'sell'
        elif current_price < lower_band:
            signal_type = 'buy'
            
        return {
            'upper_band': upper_band,
            'middle_band': middle_band,
            'lower_band': lower_band,
            'band_width': band_width,
            'signal': signal_type
        }
        
    def calculate_momentum(self, prices, period=14):
        """
        Calculate Momentum indicator
        
        Args:
            prices (list): List of closing prices
            period (int): Period for momentum
            
        Returns:
            float: Momentum value
        """
        if len(prices) <= period:
            return 0
            
        # Momentum = Current Price - Price N periods ago
        momentum = prices[-1] - prices[-period-1]
        
        return momentum
        
    def _calculate_ema(self, prices, period):
        """
        Calculate Exponential Moving Average
        
        Args:
            prices (list): List of prices
            period (int): EMA period
            
        Returns:
            float: EMA value
        """
        if isinstance(prices, list) and len(prices) < period:
            return sum(prices) / len(prices)
            
        ema = sum(prices[:period]) / period
        multiplier = 2 / (period + 1)
        
        for i in range(period, len(prices)):
            ema = (prices[i] - ema) * multiplier + ema
            
        return ema
        
    def analyze_stock(self, prices):
        """
        Comprehensive analysis of a stock based on multiple indicators
        
        Args:
            prices (list): List of closing prices
            
        Returns:
            dict: Analysis results and trading recommendations
        """
        if not prices or len(prices) < 30:
            return {
                'recommendation': 'neutral',
                'confidence': 'low',
                'indicators': {
                    'rsi': 50,
                    'macd': 'neutral',
                    'bollinger': 'neutral',
                    'momentum': 0
                }
            }
            
        # Calculate various indicators
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bollinger = self.calculate_bollinger_bands(prices)
        momentum = self.calculate_momentum(prices)
        
        # Count buy and sell signals
        buy_signals = 0
        sell_signals = 0
        
        # RSI signals
        if rsi < 30:
            buy_signals += 1
        elif rsi > 70:
            sell_signals += 1
            
        # MACD signals
        if macd['signal'] == 'buy':
            buy_signals += 1
        elif macd['signal'] == 'sell':
            sell_signals += 1
            
        # Bollinger Bands signals
        if bollinger['signal'] == 'buy':
            buy_signals += 1
        elif bollinger['signal'] == 'sell':
            sell_signals += 1
            
        # Momentum signals
        if momentum > 0:
            buy_signals += 0.5  # Weight momentum less than other indicators
        elif momentum < 0:
            sell_signals += 0.5
            
        # Determine overall recommendation
        recommendation = 'neutral'
        if buy_signals > sell_signals and buy_signals >= 2:
            recommendation = 'buy'
        elif sell_signals > buy_signals and sell_signals >= 2:
            recommendation = 'sell'
            
        # Determine confidence level
        confidence = 'low'
        signal_strength = max(buy_signals, sell_signals)
        
        if signal_strength >= 3:
            confidence = 'high'
        elif signal_strength >= 2:
            confidence = 'medium'
            
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'indicators': {
                'rsi': rsi,
                'macd': macd['signal'],
                'bollinger': bollinger['signal'],
                'momentum': momentum
            }
        }

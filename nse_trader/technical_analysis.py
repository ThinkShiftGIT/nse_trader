"""
Technical analysis module for NSE Trader application.
Contains various indicators and strategies for stock analysis.
"""
import pandas as pd
import pandas_ta as ta

class TechnicalAnalyzer:
    """
    Provides technical analysis indicators and trading signals using pandas_ta.
    """
    
    def __init__(self):
        """Initialize the technical analyzer"""
        pass
        
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index (RSI)"""
        prices_series = pd.Series(prices)
        rsi = ta.rsi(prices_series, length=period)
        return rsi.iloc[-1] if rsi is not None and not rsi.empty else 50
        
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate Moving Average Convergence Divergence (MACD)"""
        prices_series = pd.Series(prices)
        macd_df = ta.macd(prices_series, fast=fast, slow=slow, signal=signal)
        if macd_df is None or macd_df.empty:
            return {'macd_line': 0, 'signal_line': 0, 'histogram': 0, 'signal': 'neutral'}
            
        latest_macd = macd_df.iloc[-1]
        signal_type = 'neutral'
        if latest_macd[f'MACD_{fast}_{slow}_{signal}'] > latest_macd[f'MACDs_{fast}_{slow}_{signal}']:
            signal_type = 'buy'
        elif latest_macd[f'MACD_{fast}_{slow}_{signal}'] < latest_macd[f'MACDs_{fast}_{slow}_{signal}']:
            signal_type = 'sell'
            
        return {
            'macd_line': latest_macd[f'MACD_{fast}_{slow}_{signal}'],
            'signal_line': latest_macd[f'MACDs_{fast}_{slow}_{signal}'],
            'histogram': latest_macd[f'MACDh_{fast}_{slow}_{signal}'],
            'signal': signal_type
        }
        
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        prices_series = pd.Series(prices)
        bb_df = ta.bbands(prices_series, length=period, std=std_dev, ddof=0)
        if bb_df is None or bb_df.empty:
            return {'upper_band': 0, 'middle_band': 0, 'lower_band': 0, 'band_width': 0, 'signal': 'neutral'}

        latest_bb = bb_df.iloc[-1]
        signal_type = 'neutral'
        current_price = prices[-1]
        
        if current_price > latest_bb[f'BBU_{period}_{float(std_dev)}']:
            signal_type = 'sell'
        elif current_price < latest_bb[f'BBL_{period}_{float(std_dev)}']:
            signal_type = 'buy'

        return {
            'upper_band': latest_bb[f'BBU_{period}_{float(std_dev)}'],
            'middle_band': latest_bb[f'BBM_{period}_{float(std_dev)}'],
            'lower_band': latest_bb[f'BBL_{period}_{float(std_dev)}'],
            'band_width': latest_bb[f'BBB_{period}_{float(std_dev)}'],
            'signal': signal_type
        }
        
    def calculate_momentum(self, prices, period=14):
        """Calculate Momentum indicator"""
        prices_series = pd.Series(prices)
        momentum = ta.mom(prices_series, length=period)
        return momentum.iloc[-1] if momentum is not None and not momentum.empty else 0
        
    def analyze_stock(self, prices):
        """Comprehensive analysis of a stock based on multiple indicators"""
        if not prices or len(prices) < 30:
            return {
                'recommendation': 'neutral',
                'confidence': 'low',
                'indicators': {'rsi': 50, 'macd': 'neutral', 'bollinger': 'neutral', 'momentum': 0}
            }
            
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bollinger = self.calculate_bollinger_bands(prices)
        momentum = self.calculate_momentum(prices)
        
        buy_signals = 0
        sell_signals = 0
        
        if rsi < 30:
            buy_signals += 1
        elif rsi > 70:
            sell_signals += 1
            
        if macd['signal'] == 'buy':
            buy_signals += 1
        elif macd['signal'] == 'sell':
            sell_signals += 1
            
        if bollinger['signal'] == 'buy':
            buy_signals += 1
        elif bollinger['signal'] == 'sell':
            sell_signals += 1
            
        if momentum > 0:
            buy_signals += 0.5
        elif momentum < 0:
            sell_signals += 0.5
            
        recommendation = 'neutral'
        if buy_signals > sell_signals and buy_signals >= 2:
            recommendation = 'buy'
        elif sell_signals > buy_signals and sell_signals >= 2:
            recommendation = 'sell'
            
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

    def calculate_entry_exit_points(self, prices):
        """Calculate entry and exit points for a given stock."""
        if not prices:
            return {'price': 0, 'stop_loss': 0, 'take_profit': 0}

        current_price = prices[-1]
        volatility_factor = 0.05

        if current_price > 1000:
            volatility_factor = 0.03
        elif current_price > 500:
            volatility_factor = 0.04
        elif current_price < 50:
            volatility_factor = 0.08

        stop_loss = round(current_price * (1 - volatility_factor), 2)
        take_profit = round(current_price * (1 + (volatility_factor * 1.5)), 2)

        return {
            'price': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
        }

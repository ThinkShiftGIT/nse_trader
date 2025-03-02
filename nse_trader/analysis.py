"""Technical analysis module for NSE Trader."""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Handles technical analysis calculations for stock data."""
    
    def __init__(self):
        """Initialize technical analyzer."""
        self.indicators = [
            'sma_50', 'sma_200', 'ema_50', 'ema_200', 'rsi', 
            'macd', 'macd_signal', 'macd_hist', 
            'bb_upper', 'bb_middle', 'bb_lower'
        ]
    
    def analyze_stock(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators for the given stock data.
        
        Args:
            data: DataFrame with OHLCV price data
            
        Returns:
            Dictionary with calculated technical indicators
        """
        if data.empty:
            logger.warning("Empty data provided for technical analysis")
            return {}
            
        try:
            # Make a copy to avoid modifying the original
            df = data.copy()
            
            # Handle missing data
            df = df.fillna(method='ffill').fillna(method='bfill')
            
            if len(df) < 200:
                logger.warning(f"Not enough data points for full analysis: {len(df)} available")
                if len(df) < 14:  # Minimum required for RSI
                    return {}
            
            result = {}
            
            # Calculate Simple Moving Averages
            result['sma_50'] = self._calc_sma(df, 50)
            result['sma_200'] = self._calc_sma(df, 200)
            
            # Calculate Exponential Moving Averages
            result['ema_50'] = self._calc_ema(df, 50)
            result['ema_200'] = self._calc_ema(df, 200)
            
            # Calculate RSI (Relative Strength Index)
            result['rsi'] = self._calc_rsi(df)
            
            # Calculate MACD (Moving Average Convergence Divergence)
            macd_vals = self._calc_macd(df)
            result['macd'] = macd_vals['macd']
            result['macd_signal'] = macd_vals['signal']
            result['macd_hist'] = macd_vals['hist']
            
            # Calculate Bollinger Bands
            bb = self._calc_bollinger_bands(df)
            result['bb_upper'] = bb['upper']
            result['bb_middle'] = bb['middle']
            result['bb_lower'] = bb['lower']
            
            # Add trend indicators
            result['is_uptrend'] = result['sma_50'] > result['sma_200'] if 'sma_50' in result and 'sma_200' in result else None
            result['is_overbought'] = result['rsi'] > 70 if 'rsi' in result else None
            result['is_oversold'] = result['rsi'] < 30 if 'rsi' in result else None
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}
    
    def generate_signals(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on technical analysis.
        
        Args:
            analysis: Dictionary of technical indicators
            
        Returns:
            Dictionary with trading signals, strength and reasons
        """
        if not analysis:
            logger.warning("Cannot generate signals: empty analysis")
            return {
                'recommendation': 'HOLD',
                'strength': 0,
                'reasons': ['Error generating signals']
            }
            
        try:
            # Initialize strength and reasons
            strength = 0
            reasons = []
            
            # Check moving average crossover (Golden Cross / Death Cross)
            if 'sma_50' in analysis and 'sma_200' in analysis:
                if analysis['sma_50'] > analysis['sma_200']:
                    strength += 1
                    reasons.append("SMA 50 above SMA 200 (Golden Cross)")
                else:
                    strength -= 1
                    reasons.append("SMA 50 below SMA 200 (Death Cross)")
            
            # Check RSI for overbought/oversold conditions
            if 'rsi' in analysis:
                if analysis['rsi'] < 30:
                    strength += 1
                    reasons.append(f"RSI oversold at {analysis['rsi']:.1f}")
                elif analysis['rsi'] > 70:
                    strength -= 1
                    reasons.append(f"RSI overbought at {analysis['rsi']:.1f}")
            
            # Check MACD signal line crossover
            if 'macd' in analysis and 'macd_signal' in analysis:
                if analysis['macd'] > analysis['macd_signal']:
                    strength += 1
                    reasons.append("MACD above signal line")
                else:
                    strength -= 1
                    reasons.append("MACD below signal line")
            
            # Check Bollinger Bands
            if 'bb_lower' in analysis and 'bb_upper' in analysis and len(analysis.get('close', [])) > 0:
                close = analysis.get('close', [0])[-1]  # Most recent closing price
                if close < analysis['bb_lower']:
                    strength += 1
                    reasons.append("Price below lower Bollinger Band")
                elif close > analysis['bb_upper']:
                    strength -= 1
                    reasons.append("Price above upper Bollinger Band")
            
            # Generate recommendation based on strength
            recommendation = self._get_recommendation(strength)
            
            return {
                'recommendation': recommendation,
                'strength': strength,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return {
                'recommendation': 'HOLD',
                'strength': 0,
                'reasons': [f"Error: {str(e)}"]
            }
    
    def _calc_sma(self, df: pd.DataFrame, period: int) -> Optional[float]:
        """Calculate Simple Moving Average.
        
        Args:
            df: DataFrame with price data
            period: Period for SMA calculation
            
        Returns:
            Latest SMA value or None if calculation fails
        """
        try:
            if len(df) < period:
                return None
            return df['Close'].rolling(window=period).mean().iloc[-1]
        except Exception as e:
            logger.error(f"Error calculating SMA: {str(e)}")
            return None
    
    def _calc_ema(self, df: pd.DataFrame, period: int) -> Optional[float]:
        """Calculate Exponential Moving Average.
        
        Args:
            df: DataFrame with price data
            period: Period for EMA calculation
            
        Returns:
            Latest EMA value or None if calculation fails
        """
        try:
            if len(df) < period:
                return None
            return df['Close'].ewm(span=period, adjust=False).mean().iloc[-1]
        except Exception as e:
            logger.error(f"Error calculating EMA: {str(e)}")
            return None
    
    def _calc_rsi(self, df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index.
        
        Args:
            df: DataFrame with price data
            period: Period for RSI calculation (default: 14)
            
        Returns:
            Latest RSI value or None if calculation fails
        """
        try:
            if len(df) < period + 1:
                return None
                
            # Calculate price changes
            delta = df['Close'].diff()
            
            # Calculate gains and losses
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # Calculate average gain and loss
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1]
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return None
    
    def _calc_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            df: DataFrame with price data
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal EMA period (default: 9)
            
        Returns:
            Dictionary with MACD, signal and histogram values
        """
        try:
            if len(df) < slow + signal:
                return {'macd': None, 'signal': None, 'hist': None}
                
            # Calculate EMAs
            ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
            ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line.iloc[-1],
                'signal': signal_line.iloc[-1],
                'hist': histogram.iloc[-1]
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return {'macd': None, 'signal': None, 'hist': None}
    
    def _calc_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
        """Calculate Bollinger Bands.
        
        Args:
            df: DataFrame with price data
            period: Period for moving average (default: 20)
            std_dev: Number of standard deviations (default: 2.0)
            
        Returns:
            Dictionary with upper, middle and lower band values
        """
        try:
            if len(df) < period:
                return {'upper': None, 'middle': None, 'lower': None}
                
            # Calculate middle band (SMA)
            middle_band = df['Close'].rolling(window=period).mean()
            
            # Calculate standard deviation
            std = df['Close'].rolling(window=period).std()
            
            # Calculate upper and lower bands
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return {
                'upper': upper_band.iloc[-1],
                'middle': middle_band.iloc[-1],
                'lower': lower_band.iloc[-1]
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return {'upper': None, 'middle': None, 'lower': None}
    
    def _get_recommendation(self, strength: int) -> str:
        """Convert signal strength to a recommendation.
        
        Args:
            strength: Signal strength score
            
        Returns:
            Recommendation string
        """
        if strength >= 2:
            return 'STRONG BUY'
        elif strength == 1:
            return 'BUY'
        elif strength == 0:
            return 'HOLD'
        elif strength == -1:
            return 'SELL'
        else:  # strength <= -2
            return 'STRONG SELL'

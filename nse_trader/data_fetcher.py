"""Data fetching module for NSE stock data using TradingView."""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import logging
from tradingview_ta import TA_Handler, Interval

logger = logging.getLogger(__name__)

class NSEDataFetcher:
    """Handles fetching and processing of NSE stock data from TradingView."""
    
    def __init__(self):
        self.exchange = "NSENG"
        self.screener = "nigeria"
        self.interval = Interval.INTERVAL_1_DAY
        self._last_update = None
        
        # Market cap data (in billions of Naira)
        self.market_caps = {
            'MTNN': 5329.89,  # MTN Nigeria
            'DANGCEM': 4618.95,  # Dangote Cement
            'AIRTELAFRI': 4134.82,  # Airtel Africa
            'BUACEMENT': 2436.21,  # BUA Cement
            'GTCO': 882.94,  # GTCO
            'ZENITHBANK': 1099.82,  # Zenith Bank
            'NESTLE': 1190.12,  # Nestle Nigeria
            'BUAFOODS': 1085.76,  # BUA Foods
            'ACCESSCORP': 576.11,  # Access Holdings
            'UBA': 580.93,  # UBA
            'FBNH': 592.27,  # FBN Holdings
            'TRANSCORP': 203.58,  # Transcorp
            'GEREGU': 1000.0,  # Geregu Power
            'SEPLAT': 520.47,  # Seplat Energy
            'OANDO': 447.53  # Oando
        }
        
        # Trading signals explanation templates
        self.signal_explanations = {
            'STRONG_BUY': "Strong technicals with positive momentum and volume trends",
            'BUY': "Favorable price action and technical indicators suggest upside potential",
            'NEUTRAL': "Mixed signals, showing both positive and negative indicators",
            'SELL': "Technical indicators suggest downward pressure on price",
            'STRONG_SELL': "Multiple indicators showing negative momentum and selling pressure"
        }

    def get_top_stocks(self, limit: int = 10) -> List[Dict]:
        """Get top traded NSE stocks."""
        try:
            stocks_data = []
            
            for symbol in list(self.market_caps.keys())[:limit]:
                try:
                    handler = TA_Handler(
                        symbol=symbol,
                        exchange=self.exchange,
                        screener=self.screener,
                        interval=self.interval
                    )
                    analysis = handler.get_analysis()
                    
                    if analysis:
                        # Calculate market cap and other metrics
                        price = analysis.indicators.get('close', 0)
                        volume = analysis.indicators.get('volume', 0)
                        change = analysis.indicators.get('change', 0)
                        market_cap = self.market_caps.get(symbol, 0)
                        value = price * volume
                        
                        # Get recommendation and explanation
                        recommendation = analysis.summary.get('RECOMMENDATION', 'NEUTRAL')
                        explanation = self._get_recommendation_explanation(analysis)
                        
                        stocks_data.append({
                            'symbol': symbol,
                            'name': self._get_company_name(symbol),
                            'price': self._format_currency(price),
                            'price_raw': price,
                            'change': change,
                            'change_percent': f"{change:.2f}%" if change else "0.00%",
                            'volume': self._format_number(volume),
                            'volume_raw': volume,
                            'market_cap': self._format_currency(market_cap * 1e9),  # Convert billions to naira
                            'market_cap_raw': market_cap * 1e9,
                            'value': self._format_currency(value),
                            'value_raw': value,
                            'high': self._format_currency(analysis.indicators.get('high', price)),
                            'low': self._format_currency(analysis.indicators.get('low', price)),
                            'open': self._format_currency(analysis.indicators.get('open', price)),
                            'recommendation': recommendation,
                            'explanation': explanation,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {str(e)}")
                    continue
            
            # Sort by market cap
            stocks_data.sort(key=lambda x: x['market_cap_raw'], reverse=True)
            self._last_update = datetime.now()
            return stocks_data
        except Exception as e:
            logger.error(f"Error fetching top stocks: {str(e)}")
            return []

    def get_market_summary(self) -> Dict:
        """Get NSE market summary using the NGX30 index."""
        try:
            handler = TA_Handler(
                symbol="NGX30",
                exchange=self.exchange,
                screener=self.screener,
                interval=self.interval
            )
            analysis = handler.get_analysis()
            
            if not analysis:
                return {}
            
            # Calculate total market cap
            total_market_cap = sum(self.market_caps.values()) * 1e9  # Convert billions to naira
            
            # Get index value and calculate derived values
            index_value = analysis.indicators.get('close', 0)
            change = analysis.indicators.get('change', 0)
            volume = analysis.indicators.get('volume', 0)
            value = volume * analysis.indicators.get('close', 0)
            
            return {
                'asi': self._format_number(index_value, 2),
                'asi_raw': index_value,
                'change': change,
                'change_percent': f"{change:.2f}%" if change else "0.00%",
                'volume': self._format_number(volume),
                'volume_raw': volume,
                'value': self._format_currency(value),
                'value_raw': value,
                'market_cap': self._format_currency(total_market_cap),
                'market_cap_raw': total_market_cap,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_update': self._last_update.strftime("%Y-%m-%d %H:%M:%S") if self._last_update else None
            }
        except Exception as e:
            logger.error(f"Error fetching market summary: {str(e)}")
            return {}

    def _get_recommendation_explanation(self, analysis) -> str:
        """Generate a detailed explanation for the trading recommendation."""
        recommendation = analysis.summary.get('RECOMMENDATION', 'NEUTRAL')
        oscillators = analysis.oscillators.get('COMPUTE', {})
        moving_averages = analysis.moving_averages.get('COMPUTE', {})
        
        # Count signals
        ma_buy = sum(1 for x in moving_averages.values() if x == 'BUY')
        ma_sell = sum(1 for x in moving_averages.values() if x == 'SELL')
        osc_buy = sum(1 for x in oscillators.values() if x == 'BUY')
        osc_sell = sum(1 for x in oscillators.values() if x == 'SELL')
        
        # Generate explanation
        if recommendation == 'STRONG_BUY':
            return f"Strong buy signals from {ma_buy} moving averages and {osc_buy} oscillators indicate bullish momentum"
        elif recommendation == 'BUY':
            return f"Positive signals from {ma_buy} moving averages suggest upward trend"
        elif recommendation == 'STRONG_SELL':
            return f"Strong sell signals from {ma_sell} moving averages and {osc_sell} oscillators indicate bearish pressure"
        elif recommendation == 'SELL':
            return f"Negative signals from {ma_sell} moving averages suggest downward trend"
        else:
            return "Mixed signals from indicators suggest sideways movement"

    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol."""
        company_names = {
            'DANGCEM': 'Dangote Cement Plc',
            'AIRTELAFRI': 'Airtel Africa Plc',
            'MTNN': 'MTN Nigeria Communications Plc',
            'BUACEMENT': 'BUA Cement Plc',
            'NESTLE': 'Nestle Nigeria Plc',
            'GTCO': 'Guaranty Trust Holding Co Plc',
            'ZENITHBANK': 'Zenith Bank Plc',
            'FBNH': 'FBN Holdings Plc',
            'UBA': 'United Bank for Africa Plc',
            'ACCESSCORP': 'Access Holdings Plc',
            'TRANSCORP': 'Transnational Corporation Plc',
            'GEREGU': 'Geregu Power Plc',
            'SEPLAT': 'Seplat Energy Plc',
            'OANDO': 'Oando Plc',
            'BUAFOODS': 'BUA Foods Plc'
        }
        return company_names.get(symbol, symbol)

    @staticmethod
    def _format_currency(value: float) -> str:
        """Format value as Nigerian Naira."""
        if value >= 1_000_000_000_000:  # Trillion
            return f"₦{value/1_000_000_000_000:.2f}T"
        elif value >= 1_000_000_000:  # Billion
            return f"₦{value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:  # Million
            return f"₦{value/1_000_000:.2f}M"
        elif value >= 1_000:  # Thousand
            return f"₦{value/1_000:.2f}K"
        else:
            return f"₦{value:.2f}"

    @staticmethod
    def _format_number(value: float, decimals: int = 2) -> str:
        """Format large numbers with K, M, B, T suffixes."""
        if value >= 1_000_000_000_000:  # Trillion
            return f"{value/1_000_000_000_000:.{decimals}f}T"
        elif value >= 1_000_000_000:  # Billion
            return f"{value/1_000_000_000:.{decimals}f}B"
        elif value >= 1_000_000:  # Million
            return f"{value/1_000_000:.{decimals}f}M"
        elif value >= 1_000:  # Thousand
            return f"{value/1_000:.{decimals}f}K"
        else:
            return f"{value:.{decimals}f}"

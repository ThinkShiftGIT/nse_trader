# NSE Trader

A real-time Nigerian Stock Exchange (NSE) trading analysis platform that provides market insights and trading signals.

## Features

- Real-time market summary (NSE ASI, Market Cap, Volume, Value)
- Top stocks tracking with detailed analysis
- Technical analysis signals and recommendations
- Auto-refreshing data (every minute)
- Mobile-responsive design

## Technical Stack

- Backend: Python/Flask
- Frontend: HTML/JavaScript/Bootstrap
- Data Source: TradingView Technical Analysis API
- Dependency Management: Poetry

## Setup

1. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Run the application:
```bash
poetry run gunicorn -c gunicorn_config.py nse_trader.app:app
```

## Usage

The application provides:

1. Market Summary:
   - NSE All-Share Index with daily change
   - Total market capitalization
   - Trading volume and value

2. Top Stocks:
   - Real-time price updates
   - Trading signals (Buy/Sell recommendations)
   - Technical analysis explanations
   - Volume and market cap data

## Limitations

- Uses TradingView's free API tier
- Limited to top NSE stocks
- Market cap data is manually curated
- No historical data analysis

## Best Practices

- Check during market hours (10:00 AM - 2:30 PM WAT)
- Use signals as part of a broader analysis
- Consider fundamental factors
- Monitor multiple stocks for diversification

## License

Proprietary - All rights reserved
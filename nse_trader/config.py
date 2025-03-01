"""Configuration settings for the NSE Trader application."""
import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # NSE Data configuration
    DATA_DELAY_MINUTES = 15  # NSE data delay
    TOP_STOCKS_COUNT = 10    # Number of top stocks to track

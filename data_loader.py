import yfinance as yf
import alpaca_trade_api as tradeapi
import pandas as pd
try:
    import config
except ImportError:
    import config_template as config

def get_historical_data(symbol, start="2010-01-01"):
    """Fetches data from yfinance for backtesting."""
    print(f"Fetching historical data for {symbol}...")
    data = yf.download(symbol, start=start)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

def get_live_data(api, symbol, limit=50):
    """Fetches recent daily data from Alpaca for live trading."""
    print(f"Fetching recent data for {symbol} from Alpaca...")
    data = api.get_bars(symbol, '1Day', limit=limit).df
    if 'close' in data.columns:
        data = data.rename(columns={'close': 'Close'})
    return data

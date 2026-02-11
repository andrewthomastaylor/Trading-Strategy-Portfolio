import pandas as pd
import yfinance as yf
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import AssetClass
from src.api.alpaca_wrapper import AlpacaClient
from src.utils.logger import logger
from datetime import datetime

class DataProvider:
    def __init__(self, alpaca_client: AlpacaClient = None):
        self.alpaca_client = alpaca_client

    def fetch_data(self, symbol, timeframe, start, end=None, source="alpaca", asset_class=AssetClass.US_EQUITY):
        """
        Fetch historical data from specified source.
        source: "alpaca" or "yfinance"
        """
        logger.info(f"Fetching data for {symbol} from {source} ({start} to {end})")

        if source == "yfinance":
            return self._fetch_yfinance(symbol, timeframe, start, end)
        else:
            if not self.alpaca_client:
                logger.error("Alpaca client not provided for Alpaca data source.")
                return pd.DataFrame()
            return self.alpaca_client.get_historical_bars(symbol, timeframe, start, end, asset_class=asset_class)

    def fetch_extended_data(self, symbol, timeframe, years=10):
        """
        Fetch extended historical data using Yahoo Finance.
        """
        end = datetime.now()
        start = end - pd.DateOffset(years=years)
        logger.info(f"Fetching extended data for {symbol} ({years} years) from yfinance")
        return self._fetch_yfinance(symbol, timeframe, start, end)

    def fetch_fundamentals(self, symbol):
        """
        Fetch fundamental data using Yahoo Finance.
        """
        try:
            yf_symbol = symbol.replace("/", "-")
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            fundamentals = {
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "market_cap": info.get("marketCap"),
                "dividend_yield": info.get("dividendYield"),
                "revenue_growth": info.get("revenueGrowth"),
                "profit_margins": info.get("profitMargins")
            }
            return fundamentals
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return {}

    def _fetch_yfinance(self, symbol, timeframe, start, end):
        try:
            # Map Alpaca TimeFrame to YFinance interval
            interval_map = {
                TimeFrame.Minute: "1m",
                TimeFrame.Hour: "1h",
                TimeFrame.Day: "1d"
            }
            interval = interval_map.get(timeframe, "1d")

            # yfinance uses different symbol format for crypto sometimes, but let's try direct
            # BTC/USD -> BTC-USD
            yf_symbol = symbol.replace("/", "-")

            df = yf.download(yf_symbol, start=start, end=end, interval=interval, progress=False)

            if df.empty:
                return df

            # If multi-index columns (happens in newer yfinance), flatten them first
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Standardize column names to lowercase
            df.columns = [str(col).lower() for col in df.columns]

            # Rename 'adj close' to 'adj_close' if present
            if 'adj close' in df.columns:
                df = df.rename(columns={'adj close': 'adj_close'})

            return df
        except Exception as e:
            logger.error(f"Error fetching data from YFinance for {symbol}: {e}")
            return pd.DataFrame()

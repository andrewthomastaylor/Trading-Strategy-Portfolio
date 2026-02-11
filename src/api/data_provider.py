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

    def get_historical_data(self, symbol, timeframe, start=None, end=None, source="alpaca", asset_class=AssetClass.US_EQUITY, limit=None):
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

    def get_fundamentals(self, symbol):
        """
        Fetch fundamental data using Yahoo Finance.
        """
        try:
            yf_symbol = symbol.replace("/", "-")
            ticker = yf.Ticker(yf_symbol)
            # Try to fetch some fast info to check validity
            _ = ticker.fast_info
            info = ticker.info
            fundamentals = {
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "market_cap": info.get("marketCap"),
                "dividend_yield": info.get("dividendYield") / 100 if info.get("dividendYield") is not None else None,
                "revenue_growth": info.get("revenueGrowth"),
                "profit_margins": info.get("profitMargins"),
                "roe": info.get("returnOnEquity"),
                "debt_to_equity": info.get("debtToEquity"),
                "eps": info.get("trailingEps"),
                "book_value": info.get("bookValue"),
                "free_cashflow": info.get("freeCashflow")
            }
            return fundamentals
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return {}

    def get_extended_data(self, target_symbol, base_symbol, multiplier=1.0, expense_ratio=0.0, timeframe="1Day", start=None, end=None):
        """
        Extends target_symbol history using base_symbol and a multiplier.
        Similar to Testfolio functionality.
        """
        logger.info(f"Generating extended data for {target_symbol} using {base_symbol} ({multiplier}x)")

        # Get history for both
        target_df = self.get_historical_data(target_symbol, timeframe, start=start, end=end)
        base_df = self.get_historical_data(base_symbol, timeframe, start=start, end=end)

        if base_df.empty:
            return target_df

        if target_df.empty:
            # Full synthetic
            synthetic = self._generate_synthetic(base_df, multiplier, expense_ratio)
            return synthetic

        # Partial extension: Find the gap
        first_target_date = target_df.index[0]
        base_pre_gap = base_df[base_df.index < first_target_date]

        if base_pre_gap.empty:
            return target_df

        synthetic_pre_gap = self._generate_synthetic(base_pre_gap, multiplier, expense_ratio)

        # Normalize synthetic prices to match target's first price
        last_synth_price = synthetic_pre_gap['close'].iloc[-1]
        first_target_price = target_df['close'].iloc[0]
        ratio = first_target_price / last_synth_price

        synthetic_pre_gap['close'] *= ratio
        synthetic_pre_gap['open'] *= ratio
        synthetic_pre_gap['high'] *= ratio
        synthetic_pre_gap['low'] *= ratio

        combined = pd.concat([synthetic_pre_gap, target_df])
        return combined.sort_index()

    def _generate_synthetic(self, base_df, multiplier, expense_ratio):
        """
        Generates synthetic returns based on base_df
        """
        df = base_df.copy()
        returns = df['close'].pct_change().fillna(0)

        # Apply leverage and expenses (daily)
        daily_expense = (expense_ratio / 100) / 252
        synth_returns = (returns * multiplier) - daily_expense

        # Reconstruct prices
        price_factor = (1 + synth_returns).cumprod()
        initial_price = 100.0 # Arbitrary base price

        df['close'] = initial_price * price_factor
        df['open'] = df['close'].shift(1).fillna(initial_price)
        df['high'] = df['close'] # Simplified
        df['low'] = df['close']  # Simplified
        df['volume'] = 0         # Synthetic data has no real volume

        return df

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

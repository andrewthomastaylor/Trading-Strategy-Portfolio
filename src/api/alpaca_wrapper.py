import os
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
from datetime import datetime, timedelta
from src.utils.logger import logger

class AlpacaClient:
    def __init__(self, api_key=None, secret_key=None, paper=True):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        self.paper = paper

        if not self.api_key or not self.secret_key:
            logger.warning("Alpaca API keys not fully provided. Some features may not work.")
            self.trading_client = None
            self.stock_data_client = None
            self.crypto_data_client = None
        else:
            self.trading_client = TradingClient(self.api_key, self.secret_key, paper=self.paper)
            self.stock_data_client = StockHistoricalDataClient(self.api_key, self.secret_key)
            self.crypto_data_client = CryptoHistoricalDataClient(self.api_key, self.secret_key)

    def get_historical_bars(self, symbol, timeframe, start, end=None, asset_class=AssetClass.US_EQUITY):
        """
        Fetch historical bars for a symbol.
        timeframe: TimeFrame instance (e.g., TimeFrame.Day, TimeFrame.Minute)
        """
        try:
            if asset_class == AssetClass.CRYPTO:
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=[symbol],
                    timeframe=timeframe,
                    start=start,
                    end=end
                )
                bars = self.crypto_data_client.get_crypto_bars(request_params)
            else:
                request_params = StockBarsRequest(
                    symbol_or_symbols=[symbol],
                    timeframe=timeframe,
                    start=start,
                    end=end
                )
                bars = self.stock_data_client.get_stock_bars(request_params)

            df = bars.df
            if df.empty:
                return df

            # Reset index if multi-index
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)

            return df
        except Exception as e:
            logger.error(f"Error fetching historical bars for {symbol}: {e}")
            return pd.DataFrame()

    def get_account(self):
        try:
            return self.trading_client.get_account()
        except Exception as e:
            logger.error(f"Error fetching account: {e}")
            return None

    def place_market_order(self, symbol, qty, side, time_in_force=TimeInForce.GTC):
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=time_in_force
            )
            return self.trading_client.submit_order(order_data)
        except Exception as e:
            logger.error(f"Error placing market order for {symbol}: {e}")
            return None

    def place_limit_order(self, symbol, qty, side, limit_price, time_in_force=TimeInForce.GTC):
        try:
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=time_in_force,
                limit_price=limit_price
            )
            return self.trading_client.submit_order(order_data)
        except Exception as e:
            logger.error(f"Error placing limit order for {symbol}: {e}")
            return None

    def get_positions(self):
        try:
            return self.trading_client.get_all_positions()
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    def get_orders(self, status='open'):
        try:
            request_params = GetOrdersRequest(status=status)
            return self.trading_client.get_orders(request_params)
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []

    def get_asset_info(self, symbol):
        try:
            return self.trading_client.get_asset(symbol)
        except Exception as e:
            logger.error(f"Error fetching asset info for {symbol}: {e}")
            return None

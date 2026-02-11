import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
from datetime import datetime

class AlpacaClient:
    def __init__(self, api_key, secret_key, paper=True):
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.stock_client = StockHistoricalDataClient(api_key, secret_key)
        self.crypto_client = CryptoHistoricalDataClient(api_key, secret_key)

    def get_historical_bars(self, symbol, timeframe, start, end=None, asset_class=AssetClass.US_EQUITY):
        if asset_class == AssetClass.CRYPTO:
            request_params = CryptoBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=timeframe,
                start=start,
                end=end
            )
            bars = self.crypto_client.get_crypto_bars(request_params)
        else:
            request_params = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=timeframe,
                start=start,
                end=end
            )
            bars = self.stock_client.get_stock_bars(request_params)

        df = bars.df
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level=0)
        return df

    def place_market_order(self, symbol, qty, side):
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.GTC
        )
        return self.trading_client.submit_order(order_data)

    def get_account(self):
        return self.trading_client.get_account()

    def get_positions(self):
        return self.trading_client.get_all_positions()

    def get_orders(self, status='all'):
        return self.trading_client.get_orders(GetOrdersRequest(status=status))

    def get_clock(self):
        return self.trading_client.get_clock()

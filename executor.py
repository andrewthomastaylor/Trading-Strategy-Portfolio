import alpaca_trade_api as tradeapi

class AlpacaExecutor:
    def __init__(self, api_key, secret_key, base_url):
        self.api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')

    def get_current_position(self, symbol):
        """Returns current position quantity."""
        try:
            position = self.api.get_position(symbol)
            return int(position.qty)
        except:
            return 0

    def submit_market_order(self, symbol, qty, side):
        """Submits a market order."""
        print(f"Executing {side.upper()} order for {qty} shares of {symbol}...")
        return self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )

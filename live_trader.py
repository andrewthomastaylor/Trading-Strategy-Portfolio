import alpaca_trade_api as tradeapi
import pandas as pd
import time
import argparse
import schedule
from strategy import MovingAverageStrategy
from email_notifier import EmailNotifier
try:
    import config
except ImportError:
    import config_template as config

class LiveTrader:
    def __init__(self):
        self.api = tradeapi.REST(
            config.ALPACA_API_KEY,
            config.ALPACA_SECRET_KEY,
            config.ALPACA_BASE_URL,
            api_version='v2'
        )
        self.symbol = config.SYMBOL
        self.qty = config.QUANTITY
        self.strategy = MovingAverageStrategy(window=10)
        self.notifier = EmailNotifier()

    def get_data(self):
        # Get last 50 days of daily data
        barset = self.api.get_bars(self.symbol, '1Day', limit=50).df
        return barset

    def execute_trade(self):
        print(f"Checking for signals at {time.ctime()}...")
        try:
            data = self.get_data()
            if data.empty:
                print("Could not retrieve data.")
                return

            # Ensure data has 'Close' column
            if 'close' in data.columns:
                data = data.rename(columns={'close': 'Close'})

            signal = self.strategy.get_latest_signal(data)
            print(f"Latest signal for {self.symbol}: {signal}")

            # Get current position
            try:
                position = self.api.get_position(self.symbol)
                has_position = True
                curr_qty = int(position.qty)
            except:
                has_position = False
                curr_qty = 0

            if signal == 'BUY' and curr_qty == 0:
                print(f"Buying {self.qty} shares of {self.symbol}")
                self.api.submit_order(
                    symbol=self.symbol,
                    qty=self.qty,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                self.notifier.send_email(f"TRADE: BUY {self.symbol}", f"Bought {self.qty} shares of {self.symbol}")

            elif signal == 'SELL' and curr_qty > 0:
                print(f"Selling {curr_qty} shares of {self.symbol}")
                self.api.submit_order(
                    symbol=self.symbol,
                    qty=curr_qty,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                self.notifier.send_email(f"TRADE: SELL {self.symbol}", f"Sold {curr_qty} shares of {self.symbol}")

            else:
                print("No trade executed.")

        except Exception as e:
            print(f"Error executing trade: {e}")
            self.notifier.send_email("ERROR: Trading System", str(e))

def run_once():
    trader = LiveTrader()
    trader.execute_trade()

def run_scheduled():
    trader = LiveTrader()
    # Schedule at 3:45 PM ET
    # Note: This assumes server is in ET or you need to adjust
    schedule.every().day.at("15:45").do(trader.execute_trade)
    print("Trader scheduled for 3:45 PM ET daily.")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Live Trader')
    parser.add_argument('--run-once', action='store_true', help='Run the trader once')
    parser.add_argument('--schedule', action='store_true', help='Run the trader on a schedule')

    args = parser.parse_args()

    if args.run_once:
        run_once()
    elif args.schedule:
        run_scheduled()
    else:
        parser.print_help()

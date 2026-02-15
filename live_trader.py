import time
import argparse
import schedule
import alpaca_trade_api as tradeapi
from data_loader import get_live_data
from strategy import generate_signals, get_latest_action
from executor import AlpacaExecutor
from notifier import send_email_alert
import config

def trade_logic():
    print(f"--- Running Trade Logic at {time.ctime()} ---")

    # Initialize components
    api = tradeapi.REST(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, config.ALPACA_BASE_URL)
    executor = AlpacaExecutor(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, config.ALPACA_BASE_URL)

    try:
        # 1. Get Data
        data = get_live_data(api, config.SYMBOL)

        # 2. Get Signal
        df = generate_signals(data)
        action = get_latest_action(df)
        print(f"Current Signal: {action}")

        # 3. Check Position
        curr_qty = executor.get_current_position(config.SYMBOL)

        # 4. Execute
        if action == 'BUY' and curr_qty == 0:
            executor.submit_market_order(config.SYMBOL, config.QUANTITY, 'buy')
            send_email_alert(f"BUY {config.SYMBOL}", f"Bought {config.QUANTITY} shares.")

        elif action == 'SELL' and curr_qty > 0:
            executor.submit_market_order(config.SYMBOL, curr_qty, 'sell')
            send_email_alert(f"SELL {config.SYMBOL}", f"Sold {curr_qty} shares.")

        else:
            print("No action required.")

    except Exception as e:
        print(f"Error: {e}")
        send_email_alert("Trading System Error", str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-once', action='store_true')
    parser.add_argument('--schedule', action='store_true')
    args = parser.parse_args()

    if args.run_once:
        trade_logic()
    elif args.schedule:
        schedule.every().day.at("15:45").do(trade_logic)
        print("Scheduled for 3:45 PM daily.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        parser.print_help()

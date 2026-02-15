import yfinance as yf
import pandas as pd
import quantstats as qs
from strategy import MovingAverageStrategy
import os

# Extend QuantStats for better plotting
qs.extend_pandas()

def run_backtest(symbol="SPY", start="2010-01-01"):
    print(f"Downloading data for {symbol} starting from {start}...")
    data = yf.download(symbol, start=start)

    if data.empty:
        print("No data found!")
        return

    # Handle multi-index columns if yfinance returns them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    strategy = MovingAverageStrategy(window=10)
    df = strategy.calculate_signals(data)

    # Calculate returns
    df['Daily_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Daily_Return'] * df['Signal'].shift(1)

    # Generate report
    report_file = f"report_{symbol}.html"
    print(f"Generating QuantStats report: {report_file}...")
    qs.reports.html(df['Strategy_Return'], benchmark="SPY", output=report_file, title=f"{symbol} 10-Day SMA Strategy")

    print("Backtest complete!")

if __name__ == "__main__":
    run_backtest()

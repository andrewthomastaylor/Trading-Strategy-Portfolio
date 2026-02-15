import quantstats as qs
from data_loader import get_historical_data
from strategy import generate_signals

# Extend QuantStats
qs.extend_pandas()

def run_backtest(symbol="SPY", start="2010-01-01"):
    # 1. Load Data
    data = get_historical_data(symbol, start)
    if data.empty: return

    # 2. Apply Strategy
    df = generate_signals(data, window=10)

    # 3. Calculate Returns
    df['Daily_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Daily_Return'] * df['Signal'].shift(1)

    # 4. Generate Report
    report_file = f"report_{symbol}.html"
    print(f"Generating report: {report_file}...")
    qs.reports.html(df['Strategy_Return'], benchmark="SPY", output=report_file, title=f"{symbol} 10-Day SMA")
    print("Done!")

if __name__ == "__main__":
    run_backtest()

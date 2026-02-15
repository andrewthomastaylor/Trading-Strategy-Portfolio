import pandas as pd
import numpy as np

def calculate_sma(data, window=10):
    """Calculates Simple Moving Average."""
    return data['Close'].rolling(window=window).mean()

def generate_signals(data, window=10):
    """Generates signals (1 for Long, 0 for None) based on SMA."""
    df = data.copy()
    df['SMA'] = calculate_sma(df, window)

    df['Signal'] = 0.0
    start_idx = window - 1
    df.iloc[start_idx:, df.columns.get_loc('Signal')] = np.where(
        df['Close'][start_idx:] > df['SMA'][start_idx:], 1.0, 0.0
    )
    return df

def get_latest_action(df):
    """Determines the action (BUY, SELL, HOLD) based on the last two signals."""
    if len(df) < 2:
        return 'HOLD'

    curr = df['Signal'].iloc[-1]
    prev = df['Signal'].iloc[-2]

    if curr == 1.0 and prev == 0.0: return 'BUY'
    if curr == 0.0 and prev == 1.0: return 'SELL'
    return 'HOLD'

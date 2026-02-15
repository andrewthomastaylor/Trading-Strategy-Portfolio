import pandas as pd
import numpy as np

class MovingAverageStrategy:
    def __init__(self, window=10):
        self.window = window

    def calculate_signals(self, data):
        """
        Calculates signals based on 10-day moving average.
        data: pd.DataFrame with 'Close' column
        Returns: pd.DataFrame with 'SMA' and 'Signal' columns
        """
        df = data.copy()
        df['SMA'] = df['Close'].rolling(window=self.window).mean()

        # Signal: 1 if Close > SMA, 0 otherwise
        df['Signal'] = 0.0
        start_idx = self.window - 1
        df.iloc[start_idx:, df.columns.get_loc('Signal')] = np.where(
            df['Close'][start_idx:] > df['SMA'][start_idx:], 1.0, 0.0
        )

        # Position: change in Signal
        df['Position'] = df['Signal'].diff()

        return df

    def get_latest_signal(self, data):
        """
        Returns the latest signal: 'BUY', 'SELL', or 'HOLD'
        """
        df = self.calculate_signals(data)
        if len(df) < 2:
            return 'HOLD'

        current_signal = df['Signal'].iloc[-1]
        previous_signal = df['Signal'].iloc[-2]

        if current_signal == 1.0 and previous_signal == 0.0:
            return 'BUY'
        elif current_signal == 0.0 and previous_signal == 1.0:
            return 'SELL'
        else:
            return 'HOLD'

import unittest
import pandas as pd
import numpy as np
from strategy import generate_signals, get_latest_action

class TestStrategy(unittest.TestCase):
    def setUp(self):
        # Create mock data: 20 days of increasing prices
        dates = pd.date_range('2023-01-01', periods=20)
        prices = [100 + i for i in range(20)]
        self.data = pd.DataFrame({'Close': prices}, index=dates)

    def test_generate_signals(self):
        df = generate_signals(self.data, window=10)
        self.assertIn('SMA', df.columns)
        self.assertIn('Signal', df.columns)
        # SMA should be NaN for first 9 rows, valid from index 9 onwards
        self.assertTrue(np.isnan(df['SMA'].iloc[8]))
        self.assertFalse(np.isnan(df['SMA'].iloc[9]))

    def test_get_latest_action(self):
        # Signal should be Long (1.0) because price > SMA
        df = generate_signals(self.data, window=10)
        action = get_latest_action(df)
        self.assertIn(action, ['BUY', 'HOLD'])

if __name__ == '__main__':
    unittest.main()

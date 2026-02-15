import unittest
import pandas as pd
import numpy as np
from strategy import MovingAverageStrategy

class TestMovingAverageStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = MovingAverageStrategy(window=10)
        # Create mock data
        dates = pd.date_range('2023-01-01', periods=20)
        # Price going up
        prices = [100 + i for i in range(20)]
        self.data = pd.DataFrame({'Close': prices}, index=dates)

    def test_calculate_signals(self):
        df = self.strategy.calculate_signals(self.data)
        self.assertIn('SMA', df.columns)
        self.assertIn('Signal', df.columns)
        self.assertEqual(len(df), 20)
        # SMA for window 10 should be NaN for first 9 rows
        self.assertTrue(np.isnan(df['SMA'].iloc[8]))
        self.assertFalse(np.isnan(df['SMA'].iloc[9]))

    def test_get_latest_signal(self):
        # With prices always increasing, Close > SMA, so it should be BUY or HOLD
        signal = self.strategy.get_latest_signal(self.data)
        # Since it's always above, the change was at step 10. At step 20 it's HOLD.
        self.assertIn(signal, ['BUY', 'HOLD'])

if __name__ == '__main__':
    unittest.main()

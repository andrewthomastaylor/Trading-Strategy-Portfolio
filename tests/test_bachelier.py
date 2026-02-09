import unittest
import numpy as np
import pandas as pd
from bachelier.model import BachelierModel
from bachelier.strategy import BachelierTradingStrategy

class TestBachelierModel(unittest.TestCase):
    def setUp(self):
        self.s0 = 100.0
        self.sigma = 15.0
        self.r = 0.03
        self.model = BachelierModel(self.s0, self.sigma, self.r)

    def test_simulation_shape(self):
        T = 0.5
        num_steps = 10
        num_paths = 5
        S = self.model.simulate_paths(T, num_steps, num_paths)
        self.assertEqual(S.shape, (num_steps + 1, num_paths))

    def test_put_call_parity(self):
        K = 100.0
        T = 0.5
        call_price = self.model.price_european_option(K, T, 'call')
        put_price = self.model.price_european_option(K, T, 'put')

        # C - P = S0 - K * exp(-rT)
        expected_diff = self.s0 - K * np.exp(-self.r * T)
        parity_diff = (call_price - put_price) - expected_diff
        self.assertAlmostEqual(parity_diff, 0, places=7)

    def test_intrinsic_value_at_expiry(self):
        K = 105.0
        T = 0.0
        call_price = self.model.price_european_option(K, T, 'call')
        put_price = self.model.price_european_option(K, T, 'put')

        self.assertEqual(call_price, max(self.s0 - K, 0))
        self.assertEqual(put_price, max(K - self.s0, 0))

    def test_zero_volatility(self):
        K = 100.0
        T = 0.5
        no_vol_model = BachelierModel(self.s0, 0.0, self.r)
        call_price = no_vol_model.price_european_option(K, T, 'call')

        # At zero vol, call price is e^-rT * max(F-K, 0)
        F = self.s0 * np.exp(self.r * T)
        expected = np.exp(-self.r * T) * max(F - K, 0)
        self.assertAlmostEqual(call_price, expected, places=7)

    def test_strategy_signals(self):
        strategy = BachelierTradingStrategy(self.model)

        K = 100.0
        T = 0.5
        theo_call = self.model.price_european_option(K, T, 'call')

        data = {
            'strike': [K, K, K],
            'expiry': [T, T, T],
            'type': ['call', 'call', 'call'],
            'market_price': [theo_call * 0.5, theo_call * 1.6, theo_call]
        }
        df = pd.DataFrame(data)
        results = strategy.evaluate_opportunities(df)

        self.assertEqual(results.iloc[0]['signal'], 'BUY')
        self.assertEqual(results.iloc[1]['signal'], 'SELL')
        self.assertEqual(results.iloc[2]['signal'], 'HOLD')

if __name__ == '__main__':
    unittest.main()

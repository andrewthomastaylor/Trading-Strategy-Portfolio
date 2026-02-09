import unittest
import numpy as np
import pandas as pd
from trinomial.model import TrinomialTreeModel
from trinomial.strategy import TrinomialTradingStrategy

class TestTrinomialModel(unittest.TestCase):
    def setUp(self):
        self.S0 = 100.0
        self.r = 0.05
        self.sigma = 0.2
        self.model = TrinomialTreeModel(self.S0, self.r, self.sigma)

    def test_european_call_price(self):
        K = 100.0
        T = 1.0
        N = 200
        price = self.model.price_option(K, T, N, 'call', 'european')
        # Approximately Black-Scholes price: ~10.45
        self.assertAlmostEqual(price, 10.45, delta=0.05)

    def test_european_put_price(self):
        K = 100.0
        T = 1.0
        N = 200
        price = self.model.price_option(K, T, N, 'put', 'european')
        # Put-Call Parity: P = C - S0 + K*exp(-rT) = 10.45 - 100 + 100*exp(-0.05)
        # P = 10.45 - 100 + 95.1229 = 5.5729
        self.assertAlmostEqual(price, 5.57, delta=0.05)

    def test_american_put_greater_than_european(self):
        K = 100.0
        T = 1.0
        N = 100
        euro_price = self.model.price_option(K, T, N, 'put', 'european')
        amer_price = self.model.price_option(K, T, N, 'put', 'american')
        self.assertGreaterEqual(amer_price, euro_price)

    def test_put_call_parity_european(self):
        K = 100.0
        T = 1.0
        N = 200
        call_price = self.model.price_option(K, T, N, 'call', 'european')
        put_price = self.model.price_option(K, T, N, 'put', 'european')

        # C - P = S0 - K * exp(-rT)
        expected_diff = self.S0 - K * np.exp(-self.r * T)
        actual_diff = call_price - put_price
        self.assertAlmostEqual(actual_diff, expected_diff, delta=0.01)

    def test_strategy_signals(self):
        strategy = TrinomialTradingStrategy(self.model, n_steps=50)
        data = {
            'strike': [100.0, 100.0],
            'expiry': [1.0, 1.0],
            'type': ['call', 'call'],
            'style': ['european', 'european'],
            'market_price': [50.0, 1.0]
        }
        df = pd.DataFrame(data)
        results = strategy.evaluate_opportunities(df)

        self.assertEqual(results.iloc[0]['signal'], 'SELL')
        self.assertEqual(results.iloc[1]['signal'], 'BUY')

if __name__ == '__main__':
    unittest.main()

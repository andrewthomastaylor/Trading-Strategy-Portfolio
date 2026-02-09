import unittest
import numpy as np
from heston.model import HestonModel
from heston.strategy import HestonTradingStrategy

class TestHestonModel(unittest.TestCase):
    def setUp(self):
        self.s0 = 100.0
        self.v0 = 0.04
        self.kappa = 2.0
        self.theta = 0.04
        self.sigma = 0.3
        self.rho = -0.7
        self.r = 0.03
        self.model = HestonModel(self.s0, self.v0, self.kappa, self.theta, self.sigma, self.rho, self.r)

    def test_simulation_shape(self):
        T = 1.0
        num_steps = 10
        num_paths = 5
        S, V = self.model.simulate_paths(T, num_steps, num_paths)
        self.assertEqual(S.shape, (num_steps + 1, num_paths))
        self.assertEqual(V.shape, (num_steps + 1, num_paths))

    def test_call_price_positive(self):
        K = 100.0
        T = 1.0
        price = self.model.price_european_option(K, T, 'call')
        self.assertGreater(price, 0)

    def test_put_call_parity(self):
        K = 100.0
        T = 1.0
        call_price = self.model.price_european_option(K, T, 'call')
        put_price = self.model.price_european_option(K, T, 'put')

        # C - P = S0 - K * exp(-rT)
        parity_diff = (call_price - put_price) - (self.s0 - K * np.exp(-self.r * T))
        self.assertAlmostEqual(parity_diff, 0, places=5)

    def test_strategy_signals(self):
        import pandas as pd
        strategy = HestonTradingStrategy(self.model)

        # If market price is very high, signal should be SELL
        # If market price is very low, signal should be BUY
        data = {
            'strike': [100.0, 100.0],
            'expiry': [1.0, 1.0],
            'type': ['call', 'call'],
            'market_price': [50.0, 1.0]
        }
        df = pd.DataFrame(data)
        results = strategy.evaluate_opportunities(df)

        self.assertEqual(results.iloc[0]['signal'], 'SELL')
        self.assertEqual(results.iloc[1]['signal'], 'BUY')

if __name__ == '__main__':
    unittest.main()

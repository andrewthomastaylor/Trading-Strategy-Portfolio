import unittest
import numpy as np
import pandas as pd
from binomial.model import BinomialModel
from binomial.strategy import BinomialTradingStrategy

class TestBinomialModel(unittest.TestCase):
    def setUp(self):
        self.s0 = 100.0
        self.r = 0.05
        self.sigma = 0.2
        self.model = BinomialModel(self.s0, self.r, self.sigma)

    def test_european_call_put_parity(self):
        """Test Put-Call Parity for European options: C - P = S0 - K * exp(-rT)"""
        K = 100.0
        T = 1.0
        N = 200
        call_price = self.model.price_option(K, T, N, 'call', 'european')
        put_price = self.model.price_option(K, T, N, 'put', 'european')

        expected_parity = self.s0 - K * np.exp(-self.r * T)
        actual_parity = call_price - put_price

        self.assertAlmostEqual(actual_parity, expected_parity, places=3)

    def test_american_vs_european_call(self):
        """Without dividends, American call price should equal European call price."""
        K = 100.0
        T = 1.0
        N = 100
        euro_call = self.model.price_option(K, T, N, 'call', 'european')
        amer_call = self.model.price_option(K, T, N, 'call', 'american')
        self.assertAlmostEqual(euro_call, amer_call, places=7)

    def test_american_vs_european_put(self):
        """American put should be at least as valuable as European put."""
        K = 100.0
        T = 1.0
        N = 100
        euro_put = self.model.price_option(K, T, N, 'put', 'european')
        amer_put = self.model.price_option(K, T, N, 'put', 'american')

        self.assertGreaterEqual(amer_put, euro_put)

        # For deep in-the-money options, American put should be strictly greater
        # because early exercise is optimal.
        amer_put_itm = self.model.price_option(150.0, 1.0, 100, 'put', 'american')
        euro_put_itm = self.model.price_option(150.0, 1.0, 100, 'put', 'european')
        self.assertGreater(amer_put_itm, euro_put_itm)

    def test_intrinsic_value(self):
        """American options should be worth at least their intrinsic value."""
        K = 100.0
        T = 1.0
        N = 100

        # ITM Call
        s0_high = 150.0
        model_high = BinomialModel(s0_high, self.r, self.sigma)
        amer_call = model_high.price_option(K, T, N, 'call', 'american')
        self.assertGreaterEqual(amer_call, s0_high - K)

        # ITM Put
        s0_low = 50.0
        model_low = BinomialModel(s0_low, self.r, self.sigma)
        amer_put = model_low.price_option(K, T, N, 'put', 'american')
        self.assertGreaterEqual(amer_put, K - s0_low)

    def test_invalid_parameters(self):
        """Test that invalid parameters raise ValueErrors."""
        with self.assertRaises(ValueError):
            self.model.price_option(100, 1.0, 10, option_type='invalid')
        with self.assertRaises(ValueError):
            self.model.price_option(100, 1.0, 10, exercise_style='invalid')

    def test_strategy_signals(self):
        """Test BinomialTradingStrategy signal logic."""
        strategy = BinomialTradingStrategy(self.model, N=100)

        # Price for 100 strike call is ~10.45
        data = {
            'strike': [100.0, 100.0, 100.0],
            'expiry': [1.0, 1.0, 1.0],
            'type': ['call', 'call', 'call'],
            'market_price': [5.0, 20.0, 10.45] # Undervalued, Overvalued, Fair
        }
        df = pd.DataFrame(data)
        results = strategy.evaluate_opportunities(df)

        self.assertEqual(results.iloc[0]['signal'], 'BUY')
        self.assertEqual(results.iloc[1]['signal'], 'SELL')
        self.assertEqual(results.iloc[2]['signal'], 'HOLD')

if __name__ == '__main__':
    unittest.main()

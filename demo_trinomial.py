import numpy as np
import pandas as pd
from trinomial.model import TrinomialTreeModel
from trinomial.strategy import TrinomialTradingStrategy

def main():
    print("--- Trinomial Tree Options Trading Model Demo ---")

    # 1. Initialize Trinomial Model
    S0 = 100.0      # Initial stock price
    r = 0.05        # Risk-free rate (5%)
    sigma = 0.2     # Volatility (20%)

    model = TrinomialTreeModel(S0, r, sigma)
    print(f"Parameters: S0={S0}, r={r}, sigma={sigma}")

    # 2. Price European and American Options
    K = 100.0       # Strike price
    T = 1.0         # 1 year to maturity
    N = 100         # 100 steps

    euro_call = model.price_option(K, T, N, 'call', 'european')
    amer_call = model.price_option(K, T, N, 'call', 'american')
    euro_put = model.price_option(K, T, N, 'put', 'european')
    amer_put = model.price_option(K, T, N, 'put', 'american')

    print(f"\nOption Pricing (Strike={K}, T={T}):")
    print(f"European Call: {euro_call:.4f}")
    print(f"American Call: {amer_call:.4f}")
    print(f"European Put:  {euro_put:.4f}")
    print(f"American Put:  {amer_put:.4f}")

    # 3. Trading Strategy Demonstration
    strategy = TrinomialTradingStrategy(model, n_steps=100)

    # Mock options market data
    data = {
        'strike': [95, 100, 105, 95, 100, 105],
        'expiry': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        'type': ['call', 'call', 'call', 'put', 'put', 'put'],
        'style': ['european', 'european', 'european', 'american', 'american', 'american'],
        'market_price': [12.5, 10.0, 8.0, 3.5, 6.0, 9.5] # Mock market prices
    }
    options_df = pd.DataFrame(data)

    print("\nEvaluating trading opportunities:")
    results = strategy.evaluate_opportunities(options_df)
    print(results)

if __name__ == "__main__":
    main()

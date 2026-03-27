import numpy as np
import pandas as pd
from bachelier.model import BachelierModel
from bachelier.strategy import BachelierTradingStrategy

def main():
    print("--- Bachelier Option Trading Model Strategy Demo ---")

    # 1. Initialize Model
    # s0: Initial stock price
    # sigma: Normal volatility (absolute price volatility, e.g., 20.0 means +/- 20 units per sqrt(year))
    # r: Risk-free rate
    s0 = 100.0
    sigma = 15.0
    r = 0.03

    model = BachelierModel(s0, sigma, r)
    print(f"Parameters: S0={s0}, Normal Vol={sigma}, Risk-free Rate={r}")

    # 2. Simulate Paths
    T = 0.5 # 6 months
    steps = 126
    paths = 5000
    print(f"\nSimulating {paths} paths over {T} year...")
    S_paths = model.simulate_paths(T, steps, paths)
    final_prices = S_paths[-1]

    print(f"Mean Final Price: {np.mean(final_prices):.4f}")
    print(f"Expected Forward (S0*exp(rT)): {s0 * np.exp(r * T):.4f}")
    print(f"Standard Deviation of Final Prices: {np.std(final_prices):.4f}")
    print(f"Expected Std Dev (sigma*sqrt(T)): {sigma * np.sqrt(T):.4f}")

    # 3. Price an Option
    strike = 100.0
    call_price = model.price_european_option(strike, T, 'call')
    print(f"\nBachelier Call Price (K={strike}, T={T}): {call_price:.4f}")

    # Monte Carlo Validation
    mc_call_price = np.exp(-r * T) * np.mean(np.maximum(final_prices - strike, 0))
    print(f"Monte Carlo Call Price: {mc_call_price:.4f}")

    # 4. Trading Strategy
    strategy = BachelierTradingStrategy(model)

    # Mock Market Data
    market_data = {
        'strike': [90, 100, 110, 100],
        'expiry': [T, T, T, T],
        'type': ['call', 'call', 'call', 'put'],
        'market_price': [12.5, 4.0, 1.2, 3.8] # Mock prices
    }
    options_df = pd.DataFrame(market_data)

    print("\nEvaluating Opportunities:")
    results = strategy.evaluate_opportunities(options_df)
    print(results)

if __name__ == "__main__":
    main()

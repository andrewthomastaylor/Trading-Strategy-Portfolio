import numpy as np
import pandas as pd
from binomial.model import BinomialModel
from binomial.strategy import BinomialTradingStrategy

def main():
    # 1. Initialize Binomial Model
    # Parameters: s0, r, sigma
    s0 = 100.0      # Initial stock price
    r = 0.05        # Risk-free rate (5%)
    sigma = 0.2     # Volatility (20%)

    model = BinomialModel(s0, r, sigma)

    # 2. Price Options
    K = 100.0       # Strike price
    T = 1.0         # 1 year to maturity
    N = 100         # 100 steps in the binomial tree

    print(f"--- Binomial Option Pricing (CRR Model) ---")
    print(f"Parameters: S0={s0}, K={K}, T={T}, r={r}, sigma={sigma}, N={N}\n")

    euro_call = model.price_option(K, T, N, 'call', 'european')
    amer_call = model.price_option(K, T, N, 'call', 'american')
    euro_put = model.price_option(K, T, N, 'put', 'european')
    amer_put = model.price_option(K, T, N, 'put', 'american')

    print(f"European Call Price: {euro_call:.4f}")
    print(f"American Call Price: {amer_call:.4f}")
    print(f"European Put Price:  {euro_put:.4f}")
    print(f"American Put Price:  {amer_put:.4f}")
    print(f"Early Exercise Premium (Put): {amer_put - euro_put:.4f}")

    # 3. Trading Strategy Demonstration
    print(f"\n--- Binomial Trading Strategy ---")
    strategy = BinomialTradingStrategy(model, N=200)

    # Mock options market data
    data = {
        'strike': [90, 100, 110, 100],
        'expiry': [1.0, 1.0, 1.0, 1.0],
        'type': ['call', 'call', 'call', 'put'],
        'exercise_style': ['european', 'european', 'european', 'american'],
        'market_price': [14.0, 10.0, 6.0, 6.5]
    }
    options_df = pd.DataFrame(data)

    print("Evaluating trading opportunities:")
    results = strategy.evaluate_opportunities(options_df)
    print(results)

    # 4. Convergence Demonstration
    print(f"\n--- Convergence Check (European Call) ---")
    for steps in [10, 50, 100, 500, 1000]:
        price = model.price_option(K, T, steps, 'call', 'european')
        print(f"Steps: {steps:4d} | Price: {price:.4f}")

if __name__ == "__main__":
    main()

import numpy as np
import pandas as pd
from heston.model import HestonModel
from heston.strategy import HestonTradingStrategy

def main():
    # 1. Initialize Heston Model
    # Parameters: s0, v0, kappa, theta, sigma, rho, r
    s0 = 100.0      # Initial stock price
    v0 = 0.04       # Initial variance (20% vol)
    kappa = 2.0     # Mean reversion rate
    theta = 0.04    # Long-term variance
    sigma = 0.3     # Volatility of volatility
    rho = -0.7      # Correlation
    r = 0.03        # Risk-free rate

    model = HestonModel(s0, v0, kappa, theta, sigma, rho, r)

    # 2. Simulate Paths
    T = 1.0         # 1 year
    num_steps = 252 # Daily steps
    num_paths = 1000

    print(f"Simulating {num_paths} paths over {T} year(s)...")
    S_paths, V_paths = model.simulate_paths(T, num_steps, num_paths)
    print(f"Final average stock price: {np.mean(S_paths[-1]):.2f}")

    # 3. Price an Option
    strike = 100.0
    call_price = model.price_european_option(strike, T, 'call')
    print(f"Heston Closed-Form Call Price (Strike={strike}): {call_price:.4f}")

    # 4. Trading Strategy Demonstration
    strategy = HestonTradingStrategy(model)

    # Mock options market data
    data = {
        'strike': [90, 100, 110],
        'expiry': [1.0, 1.0, 1.0],
        'type': ['call', 'call', 'call'],
        'market_price': [15.0, 10.0, 5.0] # Mock prices
    }
    options_df = pd.DataFrame(data)

    print("\nEvaluating trading opportunities:")
    results = strategy.evaluate_opportunities(options_df)
    print(results)

    # 5. Validation: Monte Carlo vs Closed-Form
    mc_call_price = np.exp(-r * T) * np.mean(np.maximum(S_paths[-1] - strike, 0))
    print(f"\nValidation:")
    print(f"Monte Carlo Price: {mc_call_price:.4f}")
    print(f"Closed-Form Price: {call_price:.4f}")
    print(f"Difference: {abs(mc_call_price - call_price):.4f}")

if __name__ == "__main__":
    main()

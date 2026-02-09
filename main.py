import numpy as np
import matplotlib.pyplot as plt
from bates_strategy.backtest import Backtester

def run_demo():
    # 1. Setup Parameters
    # Market (True) Parameters - with negative jumps
    market_params = {
        'kappa': 3.0,
        'theta': 0.04,
        'sigma_v': 0.3,
        'rho': -0.7,
        'lamb': 2.0,      # 2 jumps per year on average
        'mu_j': -0.05,    # -5% mean jump
        'sigma_j': 0.05   # 5% jump volatility
    }

    # Model (Trader) Parameters - Trader underestimates jump risk
    model_params = market_params.copy()
    model_params['lamb'] = 0.5  # Trader thinks jumps are rare

    S0 = 100.0
    v0 = 0.04
    r = 0.03
    q = 0.0
    T = 0.25 # 3 month options
    dt = 1/252
    steps = 60 # 60 trading days

    print("Initializing Backtest...")
    print(f"Market Jumps: lamb={market_params['lamb']}, mu_j={market_params['mu_j']}")
    print(f"Model Jumps:  lamb={model_params['lamb']}, mu_j={model_params['mu_j']}")

    bt = Backtester(market_params, model_params, S0, v0, r, q, T, dt, steps)

    # Run strategy for a Call option
    print("Running Backtest...")
    portfolio_history = bt.run_backtest(K=105.0, option_type='call', threshold=0.02)

    # 2. Analyze Results
    final_wealth = portfolio_history[-1]
    total_return = (final_wealth / portfolio_history[0] - 1) * 100

    print("\n" + "="*30)
    print("   BATES STRATEGY REPORT")
    print("="*30)
    print(f"Initial Wealth:     $1,000,000.00")
    print(f"Final Wealth:       ${final_wealth:,.2f}")
    print(f"Total Return:       {total_return:.2f}%")
    print(f"Days Simulated:     {steps}")
    print(f"Ending Asset Price: ${bt.S_path[steps-1]:.2f}")
    print("="*30)

    # 3. Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(bt.S_path[:steps], color='blue', label='Underlying Price')
    ax1.set_ylabel('Price ($)')
    ax1.set_title('Bates Model Strategy Simulation')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(portfolio_history, color='green', label='Portfolio Value')
    ax2.set_ylabel('Wealth ($)')
    ax2.set_xlabel('Days')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig('strategy_performance.png')
    print("\nPerformance plot saved to 'strategy_performance.png'")

if __name__ == "__main__":
    np.random.seed(42) # For reproducibility
    run_demo()

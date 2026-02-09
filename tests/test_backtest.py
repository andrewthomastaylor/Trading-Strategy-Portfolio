import numpy as np
from bates_strategy.backtest import Backtester

def test_delta_hedging_pnl():
    params = {
        'kappa': 2.0,
        'theta': 0.04,
        'sigma_v': 0.1,
        'rho': -0.5,
        'lamb': 0.0,
        'mu_j': 0.0,
        'sigma_j': 0.0
    }

    bt = Backtester(params, params, 100.0, 0.04, 0.03, 0.0, 0.25, 1/252, 20)
    pnl_history = bt.run_backtest(K=100.0, threshold=-0.5)

    initial_val = pnl_history[0]
    final_val = pnl_history[-1]

    # Calculate what the value would be if we just held cash at risk-free rate
    expected_risk_free = initial_val * np.exp(0.03 * 20 / 252)
    excess_pnl = final_val - expected_risk_free

    print(f"Initial Value: {initial_val:.2f}")
    print(f"Final Value: {final_val:.2f}")
    print(f"Expected Risk-Free Value: {expected_risk_free:.2f}")
    print(f"Excess P&L after 20 days: {excess_pnl:.2f}")

    # Excess P&L should be small
    assert np.abs(excess_pnl) < 1000.0, f"Excess P&L too large: {excess_pnl}"

if __name__ == "__main__":
    print("Running test_delta_hedging_pnl...")
    test_delta_hedging_pnl()
    print("Backtest verification complete.")

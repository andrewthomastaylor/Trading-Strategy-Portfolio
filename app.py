import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from bates_strategy.backtest import Backtester

st.set_page_config(page_title="Bates Model Strategy Lab", layout="wide")

st.title("🧪 Bates Model Trading Strategy Lab")
st.markdown("""
This application allows you to explore the **Bates (1996) Model**, which extends the Heston stochastic volatility model by adding jumps to the asset price process.
""")

# Sidebar for parameters
st.sidebar.header("Market Parameters (Ground Truth)")
m_lamb = st.sidebar.slider("Jump Intensity (lambda)", 0.0, 5.0, 2.0, 0.1)
m_mu_j = st.sidebar.slider("Mean Log-Jump (mu_j)", -0.2, 0.2, -0.05, 0.01)
m_sigma_j = st.sidebar.slider("Jump Volatility (sigma_j)", 0.0, 0.2, 0.05, 0.01)

st.sidebar.header("Model Parameters (Trader's Perception)")
p_lamb = st.sidebar.slider("Perceived Intensity", 0.0, 5.0, 0.5, 0.1)

st.sidebar.header("Simulation Settings")
days = st.sidebar.number_input("Days", 10, 252, 60)
S0 = st.sidebar.number_input("Initial Price", 10.0, 1000.0, 100.0)

if st.button("🚀 Run Backtest"):
    market_params = {
        'kappa': 3.0, 'theta': 0.04, 'sigma_v': 0.3, 'rho': -0.7,
        'lamb': m_lamb, 'mu_j': m_mu_j, 'sigma_j': m_sigma_j
    }

    model_params = market_params.copy()
    model_params['lamb'] = p_lamb

    v0 = 0.04
    r = 0.03
    q = 0.0
    T = 0.25 # 3 months
    dt = 1/252

    with st.spinner("Simulating market and running strategy..."):
        bt = Backtester(market_params, model_params, S0, v0, r, q, T, dt, days)
        # We trade a call option with strike slightly OTM
        K = S0 * 1.05
        portfolio_history = bt.run_backtest(K=K, option_type='call', threshold=0.02)

    # Results
    col1, col2, col3 = st.columns(3)
    final_wealth = portfolio_history[-1]
    total_return = (final_wealth / portfolio_history[0] - 1) * 100

    col1.metric("Final Wealth", f"${final_wealth:,.2f}")
    col2.metric("Total Return", f"{total_return:.2f}%")
    col3.metric("Ending Asset Price", f"${bt.S_path[days-1]:.2f}")

    # Plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(bt.S_path[:days], color='#1f77b4', linewidth=2, label='Underlying Price')
    ax1.set_ylabel('Price ($)')
    ax1.set_title('Asset Price Path (with Jumps)')
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.plot(portfolio_history, color='#2ca02c', linewidth=2, label='Portfolio Value')
    ax2.set_ylabel('Wealth ($)')
    ax2.set_xlabel('Days')
    ax2.set_title('Delta-Hedged Strategy Performance')
    ax2.legend()
    ax2.grid(alpha=0.3)

    st.pyplot(fig)

    st.info("The strategy identifies mispricing in the option market caused by the trader's incorrect assumption about jump frequency, while maintaining a delta-neutral hedge to isolate the volatility/jump edge.")

else:
    st.write("Adjust parameters in the sidebar and click 'Run Backtest' to start.")

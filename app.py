import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from heston.model import HestonModel
from heston.strategy import HestonTradingStrategy

st.set_page_config(page_title="Heston Model Dashboard", layout="wide")

st.title("Heston Stochastic Volatility Model Dashboard")

# Sidebar for parameters
st.sidebar.header("Model Parameters")
s0 = st.sidebar.number_input("Initial Stock Price (S0)", value=100.0)
v0 = st.sidebar.number_input("Initial Variance (V0)", value=0.04, format="%.4f")
kappa = st.sidebar.number_input("Mean Reversion Rate (kappa)", value=2.0)
theta = st.sidebar.number_input("Long-term Variance (theta)", value=0.04, format="%.4f")
sigma = st.sidebar.number_input("Vol of Vol (sigma)", value=0.3)
rho = st.sidebar.slider("Correlation (rho)", -1.0, 1.0, -0.7)
r = st.sidebar.number_input("Risk-free Rate (r)", value=0.03)

st.sidebar.header("Simulation Settings")
T = st.sidebar.number_input("Time to Maturity (T)", value=1.0)
num_steps = st.sidebar.number_input("Steps", value=252)
num_paths = st.sidebar.number_input("Paths", value=100)

model = HestonModel(s0, v0, kappa, theta, sigma, rho, r)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Price Path Simulation")
    if st.button("Run Simulation"):
        S, V = model.simulate_paths(T, int(num_steps), int(num_paths))

        fig, ax = plt.subplots()
        ax.plot(S[:, :10]) # Plot first 10 paths
        ax.set_title("Asset Price Paths (First 10)")
        ax.set_xlabel("Steps")
        ax.set_ylabel("Price")
        st.pyplot(fig)

        st.write(f"Average Terminal Price: {np.mean(S[-1]):.2f}")

with col2:
    st.subheader("Option Pricing")
    strike = st.number_input("Strike Price", value=100.0)
    opt_type = st.selectbox("Option Type", ["call", "put"])

    if st.button("Calculate Price"):
        price = model.price_european_option(strike, T, opt_type)
        st.success(f"Theoretical Heston Price: {price:.4f}")

        # Simple Greeks / Sensitivity (Optional)
        st.info("Note: Price calculated using Fourier Transform (Closed-form).")

st.divider()

st.subheader("Trading Strategy")
st.write("Evaluate a set of options against the model:")

# Mock market data input
market_data = st.data_editor(pd.DataFrame({
    "strike": [90.0, 100.0, 110.0],
    "expiry": [T, T, T],
    "type": ["call", "call", "call"],
    "market_price": [15.5, 9.5, 4.5]
}))

if st.button("Analyze Opportunities"):
    strategy = HestonTradingStrategy(model)
    results = strategy.evaluate_opportunities(market_data.copy())
    st.dataframe(results)

    for _, row in results.iterrows():
        if row['signal'] == 'BUY':
            st.success(f"BUY Opportunity: Strike {row['strike']} is undervalued!")
        elif row['signal'] == 'SELL':
            st.warning(f"SELL Opportunity: Strike {row['strike']} is overvalued!")

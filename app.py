import streamlit as st
import pandas as pd
import numpy as np
from binomial.model import BinomialModel
from binomial.strategy import BinomialTradingStrategy

st.set_page_config(page_title="Binomial Option Pricing", layout="wide")

st.title("📊 Binomial Option Pricing & Trading Strategy")

st.sidebar.header("Model Parameters")

# Sidebar inputs
s0 = st.sidebar.number_input("Initial Stock Price (S0)", value=100.0, min_value=0.01)
r = st.sidebar.slider("Risk-free Rate (r)", min_value=0.0, max_value=0.20, value=0.05, step=0.01)
sigma = st.sidebar.slider("Volatility (σ)", min_value=0.01, max_value=1.0, value=0.20, step=0.01)
n_steps = st.sidebar.number_input("Number of Steps (N)", value=100, min_value=1, max_value=1000)

# Initialize Model
model = BinomialModel(s0, r, sigma)

# Section 1: Option Pricing
st.header("1. Option Pricing")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Call Options")
    strike_call = st.number_input("Strike Price (Call)", value=100.0, min_value=0.01, key="k_call")
    expiry_call = st.number_input("Time to Maturity (Years)", value=1.0, min_value=0.01, key="t_call")

    euro_call = model.price_option(strike_call, expiry_call, n_steps, 'call', 'european')
    amer_call = model.price_option(strike_call, expiry_call, n_steps, 'call', 'american')

    st.write(f"**European Call:** ${euro_call:.4f}")
    st.write(f"**American Call:** ${amer_call:.4f}")

with col2:
    st.subheader("Put Options")
    strike_put = st.number_input("Strike Price (Put)", value=100.0, min_value=0.01, key="k_put")
    expiry_put = st.number_input("Time to Maturity (Years)", value=1.0, min_value=0.01, key="t_put")

    euro_put = model.price_option(strike_put, expiry_put, n_steps, 'put', 'european')
    amer_put = model.price_option(strike_put, expiry_put, n_steps, 'put', 'american')

    st.write(f"**European Put:** ${euro_put:.4f}")
    st.write(f"**American Put:** ${amer_put:.4f}")
    st.info(f"Early Exercise Premium: ${amer_put - euro_put:.4f}")

# Section 2: Trading Strategy
st.header("2. Trading Strategy Evaluation")
st.write("Enter market prices for different options to generate signals based on the model.")

# Table for market data input
default_data = {
    'strike': [90.0, 100.0, 110.0, 100.0],
    'expiry': [1.0, 1.0, 1.0, 1.0],
    'type': ['call', 'call', 'call', 'put'],
    'exercise_style': ['european', 'european', 'european', 'american'],
    'market_price': [16.5, 10.0, 6.0, 6.5]
}
market_df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

if st.button("Generate Signals"):
    strategy = BinomialTradingStrategy(model, N=n_steps)
    results = strategy.evaluate_opportunities(market_df.copy())

    def color_signal(val):
        color = 'white'
        if val == 'BUY':
            color = 'lightgreen'
        elif val == 'SELL':
            color = 'salmon'
        return f'background-color: {color}'

    st.subheader("Results")
    # Using map instead of applymap for newer pandas versions
    st.dataframe(results.style.map(color_signal, subset=['signal']))

# Section 3: Convergence
st.header("3. Convergence Analysis")
st.write("See how the price converges as the number of steps increases.")
if st.button("Run Convergence Analysis"):
    steps_list = [10, 50, 100, 250, 500]
    convergence_results = []
    for s in steps_list:
        p = model.price_option(strike_call, expiry_call, s, 'call', 'european')
        convergence_results.append({"Steps": s, "Price": p})

    conv_df = pd.DataFrame(convergence_results)
    st.line_chart(conv_df.set_index("Steps"))
    st.table(conv_df)

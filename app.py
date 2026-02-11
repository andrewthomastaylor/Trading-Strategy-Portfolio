import streamlit as st
import pandas as pd
from trinomial.model import TrinomialTreeModel
from trinomial.strategy import TrinomialTradingStrategy

st.set_page_config(page_title="Trinomial Options Trading Model", layout="wide")

st.title("Trinomial Tree Options Trading Model")

# Sidebar for Model Parameters
st.sidebar.header("Model Parameters")
s0 = st.sidebar.number_input("Initial Stock Price (S0)", value=100.0, min_value=0.01)
r = st.sidebar.slider("Risk-free Interest Rate (r)", min_value=0.0, max_value=0.2, value=0.05, step=0.01)
sigma = st.sidebar.slider("Volatility (sigma)", min_value=0.01, max_value=1.0, value=0.2, step=0.01)
n_steps = st.sidebar.number_input("Number of Time Steps (N)", value=100, min_value=1, max_value=500)

# Initialize the model
model = TrinomialTreeModel(s0, r, sigma)

col1, col2 = st.columns(2)

with col1:
    st.header("Single Option Pricing")
    k = st.number_input("Strike Price (K)", value=100.0, min_value=0.01)
    t = st.number_input("Time to Maturity (T in years)", value=1.0, min_value=0.01)
    opt_type = st.selectbox("Option Type", ["call", "put"])
    opt_style = st.selectbox("Option Style", ["european", "american"])

    if st.button("Price Option"):
        price = model.price_option(k, t, n_steps, opt_type, opt_style)
        st.success(f"Theoretical {opt_style.capitalize()} {opt_type.capitalize()} Price: **{price:.4f}**")

with col2:
    st.header("Trading Strategy Evaluation")
    st.write("Evaluate multiple options against market prices.")

    # Pre-populated mock data
    default_data = """strike,expiry,type,style,market_price
95,1.0,call,european,12.5
100,1.0,call,european,10.0
105,1.0,call,european,8.0
95,1.0,put,american,3.5
100,1.0,put,american,6.0
105,1.0,put,american,9.5"""

    csv_input = st.text_area("Input Options Data (CSV format: strike,expiry,type,style,market_price)", value=default_data)

    if st.button("Evaluate Opportunities"):
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(csv_input))
            strategy = TrinomialTradingStrategy(model, n_steps=n_steps)
            results = strategy.evaluate_opportunities(df)

            st.dataframe(results.style.map(lambda x: 'background-color: #d4edda' if x == 'BUY' else ('background-color: #f8d7da' if x == 'SELL' else ''), subset=['signal']))

            st.info("BUY signal: Model Price > Market Price * 1.01\nSELL signal: Model Price < Market Price * 0.99")
        except Exception as e:
            st.error(f"Error processing data: {e}")

st.markdown("---")
st.markdown("### About the Model")
st.write("""
The Trinomial Tree model is a lattice-based method used for option pricing.
It's an extension of the binomial model, allowing for three possible movements in each time step: up, down, or stay the same.
This implementation uses the **Boyle (1986)** method for jump sizes and probabilities, ensuring convergence to the Black-Scholes model for European options.
It supports both **European** and **American** exercise styles.
""")

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fdm.model import FiniteDifferenceModel

st.set_page_config(page_title="FDM Option Pricing", layout="wide")

st.title("Finite Difference Method - Option Pricing")

with st.sidebar:
    st.header("Model Parameters")
    s0 = st.number_input("Current Stock Price (S0)", value=100.0, min_value=1.0)
    k = st.number_input("Strike Price (K)", value=100.0, min_value=1.0)
    t = st.number_input("Time to Maturity (T in years)", value=1.0, min_value=0.01)
    r = st.number_input("Risk-free Rate (r)", value=0.05, step=0.01)
    sigma = st.number_input("Volatility (sigma)", value=0.20, step=0.01)

    st.header("FDM Grid Settings")
    m = st.slider("Number of Price Steps (M)", 50, 500, 200)
    n = st.slider("Number of Time Steps (N)", 100, 5000, 1000)
    s_max_mult = st.slider("S_max Multiplier", 2.0, 5.0, 3.0)

col1, col2 = st.columns(2)

with col1:
    st.subheader("European Options")
    model = FiniteDifferenceModel(s_max_mult=s_max_mult, m=m, n=n)

    euro_call = model.price_option(s0, k, t, r, sigma, option_type='call', exercise_style='european')
    euro_put = model.price_option(s0, k, t, r, sigma, option_type='put', exercise_style='european')

    st.metric("European Call Price", f"{euro_call:.4f}")
    st.metric("European Put Price", f"{euro_put:.4f}")

with col2:
    st.subheader("American Options")
    amer_call = model.price_option(s0, k, t, r, sigma, option_type='call', exercise_style='american')
    amer_put = model.price_option(s0, k, t, r, sigma, option_type='put', exercise_style='american')

    st.metric("American Call Price", f"{amer_call:.4f}")
    st.metric("American Put Price", f"{amer_put:.4f}")

st.divider()

st.subheader("Price Visualization")
s_range = np.linspace(k * 0.5, k * 1.5, 50)
prices_euro_call = [model.price_option(s, k, t, r, sigma, 'call', 'european') for s in s_range]
prices_amer_call = [model.price_option(s, k, t, r, sigma, 'call', 'american') for s in s_range]
prices_euro_put = [model.price_option(s, k, t, r, sigma, 'put', 'european') for s in s_range]
prices_amer_put = [model.price_option(s, k, t, r, sigma, 'put', 'american') for s in s_range]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(s_range, prices_euro_call, label='European Call', linestyle='--')
ax1.plot(s_range, prices_amer_call, label='American Call')
ax1.set_title("Call Option Prices")
ax1.set_xlabel("Stock Price")
ax1.set_ylabel("Option Price")
ax1.legend()
ax1.grid(True)

ax2.plot(s_range, prices_euro_put, label='European Put', linestyle='--')
ax2.plot(s_range, prices_amer_put, label='American Put')
ax2.set_title("Put Option Prices")
ax2.set_xlabel("Stock Price")
ax2.set_ylabel("Option Price")
ax2.legend()
ax2.grid(True)

st.pyplot(fig)

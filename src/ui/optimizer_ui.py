import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.api.alpaca_wrapper import AlpacaClient
from src.api.data_provider import DataProvider
from src.optimization.optimizer import PortfolioOptimizer
from alpaca.data.timeframe import TimeFrame

def render_optimizer_ui():
    st.header("Portfolio Optimization")

    symbols = st.session_state.get('symbols', ["AAPL", "MSFT", "GOOG", "BTC/USD"])
    selected_symbols = st.multiselect("Select Assets for Optimization", symbols, default=symbols[:3])

    col1, col2 = st.columns(2)
    with col1:
        lookback_days = st.slider("Lookback Period (Days)", 90, 730, 365)
        method = st.selectbox("Optimization Method", ["max_sharpe", "min_volatility"])

    with col2:
        total_value = st.number_input("Total Portfolio Value ($)", value=10000.0)

    if st.button("Optimize Portfolio"):
        if not selected_symbols:
            st.warning("Please select at least one asset.")
            return

        with st.spinner("Fetching data and optimizing..."):
            client = AlpacaClient(
                st.session_state.get('alpaca_api_key'),
                st.session_state.get('alpaca_secret_key')
            )
            provider = DataProvider(client)

            end = datetime.now()
            start = end - timedelta(days=lookback_days)

            # Fetch data for all selected symbols
            price_data = {}
            for sym in selected_symbols:
                # Use yfinance for easier multi-asset fetching in this context
                df = provider.fetch_data(sym, TimeFrame.Day, start, end, source="yfinance")
                if not df.empty:
                    price_data[sym] = df['close']

            if not price_data:
                st.error("Could not fetch data for selected symbols.")
                return

            combined_df = pd.DataFrame(price_data).dropna()

            if combined_df.empty:
                st.error("Not enough overlapping data for optimization.")
                return

            optimizer = PortfolioOptimizer(combined_df)
            weights = optimizer.optimize_weights(method=method)

            if weights:
                st.subheader("Optimal Weights")
                st.json(weights)

                # Discrete allocation
                allocation, leftover = optimizer.get_discrete_allocation(weights, total_value)
                if allocation:
                    st.subheader("Discrete Allocation")
                    st.write(f"Remaining Cash: ${leftover:.2f}")
                    st.table(pd.DataFrame(allocation.items(), columns=["Asset", "Shares"]))

                # Fundamentals display for selected assets
                st.subheader("Asset Fundamentals")
                fundamentals_list = []
                for sym in selected_symbols:
                    fund = provider.fetch_fundamentals(sym)
                    fund['symbol'] = sym
                    fundamentals_list.append(fund)
                st.dataframe(pd.DataFrame(fundamentals_list).set_index('symbol'))
            else:
                st.error("Optimization failed.")

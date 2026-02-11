import streamlit as st
import pandas as pd
from src.api.alpaca_wrapper import AlpacaClient
from src.api.data_provider import DataProvider
from src.optimization.optimizer import PortfolioOptimizer
from src.utils.database import Database

def render_portfolio_optimizer():
    st.header("Portfolio Optimizer")

    db = Database()
    symbols_str = st.text_input("Symbols (comma separated)", "AAPL,MSFT,GOOGL,AMZN,TSLA")
    symbols = [s.strip() for s in symbols_str.split(",")]

    if st.button("Optimize Portfolio"):
        with st.spinner("Fetching historical data for all symbols..."):
            api_key = db.get_settings("alpaca_api_key")
            api_secret = db.get_settings("alpaca_api_secret")
            client = AlpacaClient(api_key, api_secret)
            provider = DataProvider(client)

            # Fetch closing prices for all symbols
            price_data = {}
            for symbol in symbols:
                df = provider.get_historical_data(symbol, "1Day", limit=252)
                if not df.empty:
                    price_data[symbol] = df['close']

            if not price_data:
                st.error("Could not fetch data for any symbols.")
                return

            df_prices = pd.DataFrame(price_data).dropna()

            optimizer = PortfolioOptimizer(df_prices)
            weights, perf = optimizer.optimize_mean_variance()

            if weights:
                st.subheader("Optimal Weights (Max Sharpe)")
                st.write(weights)

                st.subheader("Expected Performance")
                st.write(f"Expected Annual Return: {perf[0]*100:.2f}%")
                st.write(f"Annual Volatility: {perf[1]*100:.2f}%")
                st.write(f"Sharpe Ratio: {perf[2]:.2f}")

                st.bar_chart(pd.Series(weights))

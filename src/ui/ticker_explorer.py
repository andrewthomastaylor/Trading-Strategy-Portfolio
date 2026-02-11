import streamlit as st
import pandas as pd
from src.api.alpaca_wrapper import AlpacaClient
from src.api.data_provider import DataProvider
from src.utils.database import Database

def render_ticker_explorer():
    st.header("Ticker Explorer")

    db = Database()
    symbol = st.text_input("Enter Ticker Symbol", "AAPL").upper()

    if symbol:
        api_key = db.get_settings("alpaca_api_key")
        api_secret = db.get_settings("alpaca_api_secret")
        client = AlpacaClient(api_key, api_secret)
        provider = DataProvider(client)

        with st.spinner(f"Loading data for {symbol}..."):
            fundamentals = provider.get_fundamentals(symbol)

            if fundamentals:
                st.subheader(f"Fundamentals: {symbol}")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("P/E Ratio", f"{fundamentals.get('pe_ratio', 'N/A')}")
                col2.metric("P/B Ratio", f"{fundamentals.get('pb_ratio', 'N/A')}")
                col3.metric("ROE (%)", f"{fundamentals.get('roe', 0)*100:.2f}%" if isinstance(fundamentals.get('roe'), (int, float)) else "N/A")
                col4.metric("Div Yield", f"{fundamentals.get('dividend_yield', 0)*100:.2f}%" if isinstance(fundamentals.get('dividend_yield'), (int, float)) else "N/A")

                col5, col6, col7 = st.columns(3)
                col5.metric("Debt/Equity", f"{fundamentals.get('debt_to_equity', 'N/A')}")
                col6.metric("EPS", f"{fundamentals.get('eps', 'N/A')}")
                col7.metric("FCF", f"{fundamentals.get('free_cashflow', 0)/1e9:.2f}B" if isinstance(fundamentals.get('free_cashflow'), (int, float)) else "N/A")

            # Chart
            data = provider.get_historical_data(symbol, "1Day", limit=252)
            if not data.empty:
                st.subheader("Price History (1 Year)")
                st.line_chart(data['close'])
            else:
                st.error("No historical data available for this ticker.")

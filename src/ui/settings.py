import streamlit as st
from src.utils.database import Database
import os
import json

def render_settings(db: Database):
    st.header("Settings")

    st.subheader("Alpaca API Configuration")
    api_key = st.text_input("API Key", db.get_settings("alpaca_api_key") or "")
    api_secret = st.text_input("API Secret", db.get_settings("alpaca_api_secret") or "", type="password")
    paper = st.checkbox("Paper Trading", value=(db.get_settings("alpaca_paper") == "True"))

    if st.button("Save API Settings"):
        db.save_setting("alpaca_api_key", api_key)
        db.save_setting("alpaca_api_secret", api_secret)
        db.save_setting("alpaca_paper", str(paper))
        st.success("API settings saved!")

    st.subheader("Email Notifications (Gmail)")
    email = st.text_input("Email Address", db.get_settings("email_address") or "")
    app_pwd = st.text_input("App Password", db.get_settings("email_app_password") or "", type="password")

    if st.button("Save Email Settings"):
        db.save_setting("email_address", email)
        db.save_setting("email_app_password", app_pwd)
        st.success("Email settings saved!")

    st.subheader("Custom Ticker Extensions")
    st.info("Define reusable synthetic ticker extensions (e.g. for long-term backtesting of leveraged ETFs).")

    ext_json = db.get_settings("ticker_extensions")
    extensions = json.loads(ext_json) if ext_json else {}

    with st.expander("Add New Extension"):
        ext_symbol = st.text_input("Target Ticker (e.g. TSLL)")
        ext_base = st.text_input("Base Ticker (e.g. TSLA)")
        ext_mult = st.number_input("Multiplier", value=1.0)
        ext_exp = st.number_input("Expense Ratio (%)", value=0.0)

        if st.button("Save Extension"):
            extensions[ext_symbol] = {
                "base": ext_base,
                "multiplier": ext_mult,
                "expense_ratio": ext_exp
            }
            db.save_setting("ticker_extensions", json.dumps(extensions))
            st.success(f"Extension for {ext_symbol} saved!")

    if extensions:
        st.write("Saved Extensions:")
        st.json(extensions)
        if st.button("Clear All Extensions"):
            db.save_setting("ticker_extensions", "{}")
            st.rerun()

    st.subheader("Monitoring Control")
    from src.monitoring.manager import get_monitor
    monitor = get_monitor(db)

    col1, col2 = st.columns(2)
    if col1.button("Start Live Monitor", type="primary"):
        if monitor:
            # For demo/test, we'll use some defaults or let user select
            symbols = ["AAPL", "MSFT"] # This could be configurable
            strategy_params = {"logic": "sma_cross", "sma_fast": 50, "sma_slow": 200}
            monitor.start(symbols, "1Min", strategy_params)
            st.session_state['monitoring_active'] = True
            st.success("Monitor started!")
        else:
            st.error("Please configure Alpaca API keys first.")

    if col2.button("Stop Live Monitor"):
        if monitor:
            monitor.stop()
            st.session_state['monitoring_active'] = False
            st.warning("Monitor stopped.")

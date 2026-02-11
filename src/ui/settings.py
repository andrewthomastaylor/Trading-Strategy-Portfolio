import streamlit as st
import os
from dotenv import load_dotenv

def render_settings():
    st.header("Settings")

    with st.expander("Alpaca API Configuration", expanded=True):
        api_key = st.text_input("Alpaca API Key", value=os.getenv("ALPACA_API_KEY", ""), type="password")
        secret_key = st.text_input("Alpaca Secret Key", value=os.getenv("ALPACA_SECRET_KEY", ""), type="password")
        paper_mode = st.toggle("Paper Trading", value=True)

        if st.button("Save Alpaca Keys"):
            st.session_state['alpaca_api_key'] = api_key
            st.session_state['alpaca_secret_key'] = secret_key
            st.session_state['paper_mode'] = paper_mode
            st.session_state['db'].set_setting('alpaca_api_key', api_key)
            st.session_state['db'].set_setting('alpaca_secret_key', secret_key)
            st.session_state['db'].set_setting('paper_mode', paper_mode)
            st.success("Alpaca settings saved to DB!")

    with st.expander("Email Notifications"):
        email_sender = st.text_input("Sender Email", value=st.session_state.get('email_sender', os.getenv("EMAIL_SENDER", "")))
        email_password = st.text_input("App Password", value=st.session_state.get('email_password', os.getenv("EMAIL_APP_PASSWORD", "")), type="password")

        if st.button("Save Email Credentials"):
            st.session_state['email_sender'] = email_sender
            st.session_state['email_password'] = email_password
            st.session_state['db'].set_setting('email_sender', email_sender)
            st.session_state['db'].set_setting('email_password', email_password)
            st.success("Email settings saved to DB!")

    with st.expander("General Settings"):
        default_symbols = ",".join(st.session_state.get('symbols', ["AAPL", "MSFT", "BTC/USD"]))
        symbols = st.text_input("Trading Symbols (comma separated)", value=default_symbols)
        symbol_list = [s.strip() for s in symbols.split(",")]
        st.session_state['symbols'] = symbol_list
        st.session_state['db'].set_setting('symbols', symbol_list)

        interval = st.number_input("Monitoring Interval (minutes)", min_value=1, max_value=60, value=st.session_state.get('interval', 1))
        st.session_state['interval'] = interval
        st.session_state['db'].set_setting('interval', interval)

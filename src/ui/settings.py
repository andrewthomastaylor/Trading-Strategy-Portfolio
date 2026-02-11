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
            st.success("Alpaca settings saved to session!")

    with st.expander("Email Notifications"):
        email_sender = st.text_input("Sender Email", value=os.getenv("EMAIL_SENDER", ""))
        email_password = st.text_input("App Password", value=os.getenv("EMAIL_APP_PASSWORD", ""), type="password")

        if st.button("Save Email Credentials"):
            st.session_state['email_sender'] = email_sender
            st.session_state['email_password'] = email_password
            st.success("Email settings saved to session!")

    with st.expander("General Settings"):
        symbols = st.text_input("Trading Symbols (comma separated)", value="AAPL,MSFT,BTC/USD")
        st.session_state['symbols'] = [s.strip() for s in symbols.split(",")]

        interval = st.number_input("Monitoring Interval (minutes)", min_value=1, max_value=60, value=1)
        st.session_state['interval'] = interval

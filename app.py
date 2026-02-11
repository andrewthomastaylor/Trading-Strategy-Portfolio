import streamlit as st
from dotenv import load_dotenv
import os

# Import UI components
from src.ui.settings import render_settings
from src.ui.strategy_editor import render_strategy_editor
from src.ui.backtest_ui import render_backtest_ui
from src.ui.monitor_ui import render_monitor_ui
from src.ui.optimizer_ui import render_optimizer_ui
from src.ui.history_ui import render_history_ui
from src.utils.logger import logger
from src.utils.database import Database

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(page_title="Alpaca Algo Trading App", layout="wide")

    st.title("🚀 Alpaca Algorithmic Trading Dashboard")

    # Initialize Database
    if 'db' not in st.session_state:
        st.session_state['db'] = Database()

    db = st.session_state['db']

    # Initialize session state from DB if they don't exist
    if 'alpaca_api_key' not in st.session_state:
        st.session_state['alpaca_api_key'] = db.get_setting('alpaca_api_key', os.getenv("ALPACA_API_KEY", ""))
    if 'alpaca_secret_key' not in st.session_state:
        st.session_state['alpaca_secret_key'] = db.get_setting('alpaca_secret_key', os.getenv("ALPACA_SECRET_KEY", ""))
    if 'symbols' not in st.session_state:
        st.session_state['symbols'] = db.get_setting('symbols', ["AAPL", "MSFT", "BTC/USD"])

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a section",
        ["Live Monitoring", "Trade History", "Strategy Editor", "Backtesting", "Portfolio Optimizer", "Settings"])

    # Render the selected section
    if app_mode == "Settings":
        render_settings()
    elif app_mode == "Strategy Editor":
        render_strategy_editor()
    elif app_mode == "Backtesting":
        render_backtest_ui()
    elif app_mode == "Live Monitoring":
        render_monitor_ui()
    elif app_mode == "Portfolio Optimizer":
        render_optimizer_ui()
    elif app_mode == "Trade History":
        render_history_ui()

if __name__ == "__main__":
    main()

import streamlit as st
from src.ui.dashboard import render_dashboard
from src.ui.strategy_editor import render_strategy_editor
from src.ui.backtest_runner import render_backtest_runner
from src.ui.portfolio_optimizer import render_portfolio_optimizer
from src.ui.settings import render_settings
from src.ui.ticker_explorer import render_ticker_explorer
from src.utils.database import Database
from src.utils.logger import logger

st.set_page_config(page_title="Alpaca Algo Trader", layout="wide")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "Dashboard",
        "Ticker Explorer",
        "Strategy Editor",
        "Backtest Runner",
        "Portfolio Optimizer",
        "Settings"
    ])

    db = Database()

    if page == "Dashboard":
        render_dashboard(db)
    elif page == "Ticker Explorer":
        render_ticker_explorer()
    elif page == "Strategy Editor":
        render_strategy_editor(db)
    elif page == "Backtest Runner":
        render_backtest_runner(db)
    elif page == "Portfolio Optimizer":
        render_portfolio_optimizer()
    elif page == "Settings":
        render_settings(db)

if __name__ == "__main__":
    main()

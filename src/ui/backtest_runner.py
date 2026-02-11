import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.api.alpaca_wrapper import AlpacaClient
from src.api.data_provider import DataProvider
from src.strategies.indicator_strategy import IndicatorStrategy
from src.backtesting.engine import BacktestEngine
from src.utils.database import Database
import json

def render_backtest_runner(db: Database):
    st.header("Backtest Runner")

    # Load strategies
    strategies_json = db.get_settings("strategies")
    strategies = json.loads(strategies_json) if strategies_json else {}

    if not strategies:
        st.warning("No strategies defined. Go to Strategy Editor first.")
        return

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Symbol", "AAPL").upper()

        # Check for saved extensions
        ext_json = db.get_settings("ticker_extensions")
        saved_extensions = json.loads(ext_json) if ext_json else {}
        default_ext = saved_extensions.get(symbol, {"base": "SPY", "multiplier": 1.0, "expense_ratio": 0.0})

        with st.expander("Ticker Extension (Optional)"):
            use_extension = st.checkbox("Extend History (e.g. for Leveraged ETFs)", value=(symbol in saved_extensions))
            base_asset = st.text_input("Base Asset", default_ext["base"])
            multiplier = st.number_input("Multiplier", value=float(default_ext["multiplier"]), step=0.1)
            expense_ratio = st.number_input("Expense Ratio (%)", value=float(default_ext["expense_ratio"]), step=0.01)

        strategy_name = st.selectbox("Select Strategy", list(strategies.keys()))
        timeframe = st.selectbox("Timeframe", ["1Min", "5Min", "15Min", "1Hour", "1Day"], index=4)

    with col2:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
        end_date = st.date_input("End Date", datetime.now())
        initial_cash = st.number_input("Initial Cash", 1000, 1000000, 10000)

    if st.button("Run Backtest"):
        with st.spinner("Fetching data and running simulation..."):
            # Initialize API
            api_key = db.get_settings("alpaca_api_key")
            api_secret = db.get_settings("alpaca_api_secret")
            paper = db.get_settings("alpaca_paper") == "True"

            client = AlpacaClient(api_key, api_secret, paper)
            provider = DataProvider(client)

            # Get Data
            if use_extension:
                data = provider.get_extended_data(
                    symbol, base_asset, multiplier, expense_ratio,
                    timeframe, start=start_date.isoformat(), end=end_date.isoformat()
                )
            else:
                data = provider.get_historical_data(symbol, timeframe,
                                                start=start_date.isoformat(),
                                                end=end_date.isoformat())

            if data.empty:
                st.error("No data found for the given parameters.")
                return

            # Run Strategy
            strat_data = strategies[strategy_name]
            strategy = IndicatorStrategy(strategy_name, strat_data['params'])

            engine = BacktestEngine(strategy, data)
            portfolio = engine.run(initial_cash=initial_cash)

            # Results
            st.subheader(f"Results: {strategy_name} on {symbol}")
            metrics = engine.get_metrics()
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Total Return", metrics["Total Return"])
            m_col2.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
            m_col3.metric("Max Drawdown", metrics["Max Drawdown"])
            m_col4.metric("Win Rate", metrics["Win Rate"])

            # Chart
            st.plotly_chart(portfolio.plot(), use_container_width=True)

            if st.button("Generate HTML Report"):
                engine.generate_report("backtest_report.html")
                st.success("Report generated: backtest_report.html")

            # Monte Carlo
            st.subheader("Monte Carlo Simulation")
            sims = engine.run_monte_carlo()
            if sims is not None:
                st.line_chart(sims)

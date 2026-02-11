import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.api.alpaca_wrapper import AlpacaClient
from src.api.data_provider import DataProvider
from src.backtesting.engine import BacktestEngine
from alpaca.data.timeframe import TimeFrame
import plotly.graph_objects as go
import quantstats as qs

def render_backtest_ui():
    st.header("Backtesting")

    if 'current_strategy' not in st.session_state:
        st.warning("Please define a strategy in the Strategy Editor first.")
        return

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox("Symbol", st.session_state.get('symbols', ["AAPL", "BTC/USD"]))
        data_source = st.radio("Data Source", ["alpaca", "yfinance"], horizontal=True)
        days_back = st.slider("Days Back", 30, 3650, 365)

    with col2:
        fees = st.number_input("Fees (decimal)", value=0.001, format="%.4f")
        slippage = st.number_input("Slippage (decimal)", value=0.001, format="%.4f")
        extend_backtest = st.checkbox("Extend Backtest (Use max history from YFinance)", value=False)

    if st.button("Run Backtest"):
        with st.spinner("Fetching data and running backtest..."):
            client = AlpacaClient(
                st.session_state.get('alpaca_api_key'),
                st.session_state.get('alpaca_secret_key')
            )

            provider = DataProvider(client)

            end = datetime.now()
            start = end - timedelta(days=days_back)

            # Simple heuristic for asset class
            from alpaca.trading.enums import AssetClass
            asset_class = AssetClass.CRYPTO if "/" in symbol else AssetClass.US_EQUITY

            if extend_backtest:
                data = provider.fetch_extended_data(symbol, TimeFrame.Day, years=20)
                st.info(f"Using extended data from Yahoo Finance for {symbol}")
            else:
                data = provider.fetch_data(symbol, TimeFrame.Day, start, end, source=data_source, asset_class=asset_class)

            if data.empty:
                st.error(f"No data found for {symbol}")
                return

            strategy = st.session_state['current_strategy']

            fundamentals = provider.fetch_fundamentals(symbol)
            signals = strategy.generate_signals(data, fundamentals=fundamentals)

            engine = BacktestEngine(data)
            pf = engine.run_strategy(signals, fees=fees, slippage=slippage)

            if pf:
                st.subheader("Performance Metrics")
                stats = pf.stats()
                st.dataframe(stats)

                st.subheader("Robust Return Analysis (QuantStats)")
                returns = engine.get_quantstats_report()

                # Show key metrics in columns
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Sharpe Ratio", f"{qs.stats.sharpe(returns):.2f}")
                m2.metric("Sortino Ratio", f"{qs.stats.sortino(returns):.2f}")
                m3.metric("Max Drawdown", f"{qs.stats.max_drawdown(returns)*100:.2f}%")
                m4.metric("Win Rate", f"{qs.stats.win_rate(returns)*100:.2f}%")

                # Full Tear Sheet (Snapshot)
                st.subheader("QuantStats Snapshot")
                fig_qs = qs.plots.snapshot(returns, show=False)
                st.pyplot(fig_qs)

                st.subheader("Cumulative Returns")
                # pf.plot() returns a plotly figure
                fig = pf.plot()
                st.plotly_chart(fig)

                st.subheader("Monte Carlo Simulation")
                mc_results = engine.run_monte_carlo(n_simulations=50, n_days=30)
                if mc_results is not None:
                    fig_mc = go.Figure()
                    for col in mc_results.columns:
                        fig_mc.add_trace(go.Scatter(y=mc_results[col], mode='lines', line=dict(width=1), opacity=0.3))
                    fig_mc.update_layout(title="Monte Carlo: 50 Simulations (30 Days Out)", xaxis_title="Days", yaxis_title="Price")
                    st.plotly_chart(fig_mc)
            else:
                st.error("Backtest failed.")

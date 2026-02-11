# Alpaca Algorithmic Trading Platform

A comprehensive Python-based algorithmic trading application with a Streamlit UI, integrated with Alpaca API for stocks and crypto.

## Features

- **Strategy Builder**: Define technical (SMA, EMA, RSI, MACD, etc.) and fundamental (P/E, ROE, Debt/Equity) logic.
- **Advanced Backtesting**: Vectorized backtesting with `vectorbt`.
- **Ticker Extension**: Support for "extended tickers" (e.g., backtest `TSLL` using `TSLA` history with a multiplier), similar to Testfolio.
- **Monte Carlo Simulation**: Risk analysis via price path simulations.
- **Portfolio Optimization**: Mean-Variance Optimization using `PyPortfolioOpt`.
- **Live Monitoring**: Background threading for real-time signal generation and trade logging.
- **Ticker Explorer**: Research tool for technical and fundamental data.
- **Email Alerts**: Integration with Gmail for signal and error notifications.
- **Persistence**: SQLite database for settings, strategies, and trade history.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `.env.template` to `.env`.
   - Add your Alpaca API Key, Secret, and Email credentials.

3. **Run the Application**:
   - **Linux/Mac**: `./run.sh`
   - **Windows**: `run.bat`
   - **Manual**: `PYTHONPATH=. streamlit run app.py`

## Project Structure

- `src/api`: Alpaca and Data providers.
- `src/strategies`: Strategy logic and indicator calculations.
- `src/backtesting`: Simulation engine and Monte Carlo logic.
- `src/monitoring`: Background live monitoring service.
- `src/ui`: Streamlit dashboard components.
- `src/utils`: Database and Logger.

## Extended Tickers
Define synthetic extensions in the **Settings** tab. For example, to backtest a 2x Tesla ETF before its inception, map `TSLL` to `TSLA` with a 2.0 multiplier. The system will automatically stitch historical data.

## Disclaimer
Trading involves risk. This software is for educational and research purposes. Always use Paper Trading mode before deploying live capital.

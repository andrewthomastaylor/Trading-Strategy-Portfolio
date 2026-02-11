# Alpaca Algorithmic Trading App

A comprehensive Python-based algorithmic trading application that integrates with the Alpaca API for stocks and crypto.

## Features
- **Strategy Building**: UI to define custom strategies using technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands).
- **Backtesting**: Vectorized backtesting using `vectorbt` with historical data from Alpaca.
- **Monte Carlo Simulations**: Risk analysis via random return simulations.
- **Portfolio Optimization**: Mean-variance optimization using `PyPortfolioOpt`.
- **Live Monitoring**: Background monitoring of live/paper data with automated trade execution.
- **Email Alerts**: Real-time notifications for trades and errors via Gmail.
- **Streamlit UI**: Interactive dashboard for all interactions.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Create a `.env` file based on `.env.template` and add your Alpaca API keys and Email credentials.

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Project Structure
- `src/api`: Alpaca API integration.
- `src/strategies`: Strategy definitions and logic.
- `src/backtesting`: Backtesting engine.
- `src/optimization`: Portfolio optimization.
- `src/monitoring`: Live monitoring background tasks.
- `src/notifications`: Email alert service.
- `src/ui`: Streamlit dashboard components.

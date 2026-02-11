# 🚀 Alpaca Algorithmic Trading Platform

A comprehensive, production-grade algorithmic trading application built with Python and Streamlit. This platform integrates with the **Alpaca API** for execution and **Yahoo Finance** for redundant data and fundamental metrics, allowing you to build, backtest, and deploy custom trading strategies end-to-end.

---

## 📑 Table of Contents
- [Quick Start](#-quick-start)
- [Feature Walkthrough](#-feature-walkthrough)
    - [1. Strategy Editor](#1-strategy-editor)
    - [2. Backtesting Engine](#2-backtesting-engine)
    - [3. Portfolio Optimizer](#3-portfolio-optimizer)
    - [4. Live Monitoring & Trading](#4-live-monitoring--trading)
    - [5. Trade History & Logic Trace](#5-trade-history--logic-trace)
- [Technical Stack](#-technical-stack)
- [Modular Architecture](#-modular-architecture)
- [Configuration](#-configuration)

---

## ⚡ Quick Start

1.  **Clone the Repository**
2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Ensure you have the `TA-Lib` C-library installed on your system if you encounter errors during installation.*
3.  **Setup Environment Variables**
    Create a `.env` file from the template:
    ```bash
    cp .env.template .env
    ```
    Add your Alpaca API Keys and Gmail App Password for alerts.
4.  **Run the Dashboard**
    ```bash
    streamlit run app.py
    ```

---

## 🔍 Feature Walkthrough

### 1. Strategy Editor
The **Strategy Editor** is where you define your trading logic.
-   **Technical Indicators**: Use a wide range of indicators powered by `TA-Lib` (SMA, EMA, RSI, MACD, etc.).
-   **Structured Logic (AND/OR)**: Add multiple buy and sell conditions. For example, "Buy if RSI < 30 **AND** Price > SMA(200)".
-   **Fundamental Filters**: Incorporate real-time fundamentals like **P/E Ratio**, **Forward P/E**, and **Dividend Yield** directly into your entry/exit rules.
-   **Persistence**: Strategies are saved to a local SQLite database, so your configuration remains even after restarting the app.

### 2. Backtesting Engine
Test your ideas against historical data before risking capital.
-   **Redundant Data Sourcing**: Toggle between **Alpaca** and **Yahoo Finance** for historical bars.
-   **Extended History**: Automatically pull up to 20 years of history via Yahoo Finance to see how your strategy performed through different market cycles.
-   **Robust Metrics (QuantStats)**: View a full "tear sheet" including Sharpe Ratio, Sortino Ratio, Win Rate, and Max Drawdown.
-   **Risk Analysis (Monte Carlo)**: Run 50+ simulations of future price paths based on historical volatility to estimate potential range outcomes.
-   **Realistic Settings**: Define custom **Fees** and **Slippage** to ensure backtest results are grounded in reality.

### 3. Portfolio Optimizer
Optimize your asset allocation using Modern Portfolio Theory.
-   **Efficient Frontier**: Select multiple assets (stocks or crypto) and find the optimal weights for **Maximum Sharpe Ratio** or **Minimum Volatility**.
-   **Discrete Allocation**: Input your total capital, and the optimizer will calculate exactly how many shares of each asset to buy, accounting for remaining cash.
-   **Fundamental Insights**: View a consolidated table of P/E ratios and market caps for all selected assets during the optimization process.

### 4. Live Monitoring & Trading
Deploy your strategy for persistent, background execution.
-   **Background Daemon**: The monitoring engine runs in a separate thread. You can close the browser or navigate the dashboard while it continues to watch the markets.
-   **Market Hours Awareness**: The monitor automatically checks the Alpaca market clock and pauses operations during weekends, holidays, or after-hours.
-   **Automated Execution**: Places market orders automatically based on your strategy signals.
-   **Dynamic Quantities**: Calculates trade size based on a configurable percentage (default 5%) of your **actual account equity**.
-   **Email Alerts**: Receive real-time notifications via Gmail for every trade execution, order failure, or critical system error.

### 5. Trade History & Logic Trace
Total transparency into every automated decision.
-   **Trade Logs**: A searchable history of all buys and sells, stored permanently in the local database.
-   **Logic Trace**: For every trade, the system logs the **exact reason** it was triggered (e.g., "Strategy RSI_Cross generated 1 signal").
-   **Real-time Dashboard**: The "Live Monitoring" tab shows a table of the current technical indicator values for all tracked symbols, refreshed every interval.

---

## 🛠 Technical Stack

-   **Frontend**: Streamlit (Dashboard UI)
-   **Execution**: Alpaca-py (Official Alpaca SDK)
-   **Data**: yfinance (Yahoo Finance API)
-   **Analysis**: vectorbt (Vectorized Backtesting), QuantStats (Performance Metrics)
-   **Optimization**: PyPortfolioOpt (Mean-Variance Optimization)
-   **Indicators**: TA-Lib (Technical Analysis Library)
-   **Database**: SQLite (Persistence)

---

## 📂 Modular Architecture

-   `src/api/`: Handles authentication and data retrieval abstraction (`DataProvider`).
-   `src/strategies/`: Contains the abstract `BaseStrategy` and the `IndicatorStrategy` evaluator.
-   `src/backtesting/`: Logic for running simulations and generating visualizations.
-   `src/optimization/`: Portfolio weight calculation and share allocation.
-   `src/monitoring/`: The `LiveMonitor` background loop and trading logic.
-   `src/notifications/`: Email service integration.
-   `src/ui/`: Modular Streamlit components for each dashboard tab.
-   `src/utils/`: Database and Logging utilities.

---

## ⚙️ Configuration

Use the **Settings** tab to configure:
1.  **Alpaca Keys**: Toggle between Paper and Live accounts.
2.  **Email**: Enter your sender email and Gmail app password.
3.  **Symbols**: Define the list of symbols you want the platform to track and trade.
4.  **Interval**: Set the monitoring frequency (e.g., every 1 minute or every 5 minutes).

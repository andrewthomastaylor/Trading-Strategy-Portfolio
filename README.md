# Simplified Algorithmic Trading System

A modular and easy-to-understand algorithmic trading system using Alpaca.

## Architecture (Modular Chunks)
- `strategy.py`: Pure logic for signal generation (10-day SMA).
- `data_loader.py`: Handles data fetching from yfinance (backtest) and Alpaca (live).
- `executor.py`: Handles order execution on Alpaca.
- `notifier.py`: Simple email alert system.
- `backtester.py`: Orchestrates historical testing and reporting.
- `live_trader.py`: Orchestrates live trading and scheduling.

## Quick Start
1. **Setup**:
   ```bash
   python setup.py
   ```
2. **Configure**:
   Edit `config.py` with your Alpaca API Keys and Email settings.
3. **Backtest**:
   ```bash
   python backtester.py
   ```
4. **Live Trade**:
   ```bash
   python live_trader.py --run-once
   ```

## Design Principles
- **Separation of Concerns**: Each script does exactly one thing.
- **Pure Functions**: Strategy logic is decoupled from data fetching and execution.
- **Minimal Dependencies**: Uses standard libraries where possible.

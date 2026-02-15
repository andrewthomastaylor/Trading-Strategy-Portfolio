# Algorithmic Trading System

A complete algorithmic trading system using Alpaca API with a 10-day moving average strategy.

## Features
- **Strategy**: 10-day Moving Average (SMA).
- **Backtesting**: Comprehensive reports using QuantStats (2010 to present).
- **Live Trading**: Support for paper and live trading via Alpaca.
- **Notifications**: Email alerts for trades and system errors.
- **Scheduling**: Automated daily execution.

## File Structure
- `strategy.py`: Strategy logic.
- `backtester.py`: Backtesting script.
- `live_trader.py`: Live trading script.
- `email_notifier.py`: Email notification module.
- `config_template.py`: Template for configuration.
- `setup.py`: Automated setup script.

## Quick Start
1. **Setup**:
   ```bash
   python setup.py
   ```
2. **Configure**:
   Edit `config.py` and add your Alpaca API Key, Secret, and Gmail credentials.
3. **Backtest**:
   ```bash
   python backtester.py
   ```
   This generates a `report_SPY.html` file.
4. **Live Trade (Paper)**:
   ```bash
   python live_trader.py --run-once
   ```
5. **Schedule**:
   ```bash
   python live_trader.py --schedule
   ```

## Requirements
- Python 3.x
- Alpaca Trade API
- Pandas, Numpy
- QuantStats
- yfinance
- Schedule

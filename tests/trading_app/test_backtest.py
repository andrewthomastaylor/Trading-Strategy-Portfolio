import pytest
import pandas as pd
import numpy as np
from src.backtesting.engine import BacktestEngine

def test_backtest_engine():
    data = pd.DataFrame({
        'close': np.linspace(100, 150, 100),
    }, index=pd.date_range(start='2023-01-01', periods=100))

    engine = BacktestEngine(data)
    signals = pd.Series(0, index=data.index)
    signals.iloc[10] = 1 # Buy
    signals.iloc[20] = -1 # Sell

    pf = engine.run_strategy(signals, fees=0.002, slippage=0.005)
    assert pf is not None

    returns = engine.get_quantstats_report()
    assert returns is not None

    mc = engine.run_monte_carlo(n_simulations=10, n_days=5)
    assert mc is not None
    assert mc.shape == (5, 10)

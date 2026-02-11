import pytest
import pandas as pd
import numpy as np
from src.strategies.indicator_strategy import IndicatorStrategy

def test_indicator_strategy_rsi():
    # Create dummy data
    data = pd.DataFrame({
        'close': np.linspace(100, 150, 100),
        'high': np.linspace(105, 155, 100),
        'low': np.linspace(95, 145, 100),
        'open': np.linspace(100, 150, 100),
        'volume': np.ones(100) * 1000
    })

    strategy = IndicatorStrategy(params={'logic': 'rsi_sma', 'rsi_oversold': 30})
    indicators = strategy.get_indicators(data)

    assert 'rsi' in indicators.columns
    assert 'sma_fast' in indicators.columns

    signals = strategy.generate_signals(data)
    assert isinstance(signals, pd.Series)
    assert len(signals) == len(data)

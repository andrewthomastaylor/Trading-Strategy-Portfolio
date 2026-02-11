import pandas as pd
import numpy as np
from src.strategies.indicator_strategy import IndicatorStrategy

def test_indicator_signals():
    # Mock data
    data = pd.DataFrame({
        'close': [100 + i for i in range(100)],
        'open': [100 + i for i in range(100)],
        'high': [101 + i for i in range(100)],
        'low': [99 + i for i in range(100)],
        'volume': [1000] * 100
    }, index=pd.date_range('2023-01-01', periods=100))

    params = {
        "rsi_period": 14,
        "sma_fast": 20,
        "sma_slow": 50,
        "min_pe": 0,
        "max_pe": 100,
        "min_roe": 0
    }

    strategy = IndicatorStrategy("Test", params)
    signals = strategy.generate_signals(data)

    assert len(signals) == 100
    assert isinstance(signals, pd.Series)
    print("Strategy test passed.")

if __name__ == "__main__":
    test_indicator_signals()

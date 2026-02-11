import pytest
import pandas as pd
import numpy as np
from src.optimization.optimizer import PortfolioOptimizer

def test_portfolio_optimizer():
    # Create data with a clear upward trend for at least one asset to ensure Sharpe optimization works
    data = pd.DataFrame({
        'AAPL': np.linspace(100, 150, 100) + np.random.randn(100),
        'MSFT': np.linspace(200, 210, 100) + np.random.randn(100),
        'GOOG': np.linspace(150, 140, 100) + np.random.randn(100),
    }, index=pd.date_range(start='2023-01-01', periods=100))

    optimizer = PortfolioOptimizer(data)
    weights = optimizer.optimize_weights(method="max_sharpe")

    assert weights is not None
    assert 'AAPL' in weights
    assert abs(sum(weights.values()) - 1.0) < 0.01

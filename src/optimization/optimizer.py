from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns
import pandas as pd
from src.utils.logger import logger

class PortfolioOptimizer:
    def __init__(self, data: pd.DataFrame):
        """
        data: DataFrame with columns as tickers and daily closing prices
        """
        self.data = data

    def optimize_mean_variance(self):
        try:
            logger.info("Optimizing portfolio weights using Mean-Variance Optimization")
            mu = expected_returns.mean_historical_return(self.data)
            S = risk_models.sample_cov(self.data)

            ef = EfficientFrontier(mu, S)
            weights = ef.max_sharpe()
            cleaned_weights = ef.clean_weights()

            perf = ef.portfolio_performance(verbose=False)
            return cleaned_weights, perf
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return None, None

import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from src.utils.logger import logger

class PortfolioOptimizer:
    def __init__(self, price_data: pd.DataFrame):
        """
        price_data: DataFrame with dates as index and tickers as columns.
        """
        self.price_data = price_data

    def optimize_weights(self, method="max_sharpe"):
        try:
            # Calculate expected returns and sample covariance
            mu = expected_returns.mean_historical_return(self.price_data)
            S = risk_models.sample_cov(self.price_data)

            # Optimize for maximal Sharpe ratio
            ef = EfficientFrontier(mu, S)

            if method == "max_sharpe":
                weights = ef.max_sharpe()
            elif method == "min_volatility":
                weights = ef.min_volatility()
            else:
                weights = ef.max_sharpe()

            cleaned_weights = ef.clean_weights()
            return cleaned_weights
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return None

    def get_discrete_allocation(self, weights, total_portfolio_value):
        try:
            latest_prices = get_latest_prices(self.price_data)
            da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=total_portfolio_value)
            allocation, leftover = da.lp_portfolio()
            return allocation, leftover
        except Exception as e:
            logger.error(f"Error calculating discrete allocation: {e}")
            return None, None

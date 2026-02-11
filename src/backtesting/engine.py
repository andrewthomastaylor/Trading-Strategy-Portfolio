import vectorbt as vbt
import pandas as pd
import numpy as np
import quantstats as qs
from src.utils.logger import logger

class BacktestEngine:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.pf = None

    def run_strategy(self, signals: pd.Series, init_cash=10000, fees=0.001, slippage=0.001):
        """
        Run backtest using signals.
        signals: 1 for buy, -1 for sell, 0 for hold.
        """
        try:
            # Convert signals to entries and exits for vectorbt
            entries = signals == 1
            exits = signals == -1

            self.pf = vbt.Portfolio.from_signals(
                self.data['close'],
                entries,
                exits,
                init_cash=init_cash,
                fees=fees,
                slippage=slippage,
                freq='D' # Default frequency, can be adjusted
            )
            return self.pf
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return None

    def get_stats(self):
        if self.pf:
            return self.pf.stats()
        return None

    def plot_results(self):
        if self.pf:
            return self.pf.plot()
        return None

    def get_quantstats_report(self):
        """
        Return quantstats metrics and plots.
        """
        if self.pf is None:
            return None

        returns = self.pf.returns()
        # Quantstats expects a Series with datetime index
        return returns

    def run_monte_carlo(self, n_simulations=100, n_days=252):
        """
        Run Monte Carlo simulations based on historical returns.
        """
        try:
            returns = self.data['close'].pct_change().dropna()
            if returns.empty:
                return None

            # Simple Monte Carlo: Randomly sample historical returns
            simulations = np.zeros((n_days, n_simulations))
            last_price = self.data['close'].iloc[-1]

            for i in range(n_simulations):
                random_returns = np.random.choice(returns, size=n_days, replace=True)
                price_path = last_price * (1 + random_returns).cumprod()
                simulations[:, i] = price_path

            return pd.DataFrame(simulations)
        except Exception as e:
            logger.error(f"Error running Monte Carlo simulation: {e}")
            return None

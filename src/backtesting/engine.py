import vectorbt as vbt
import pandas as pd
import numpy as np
import quantstats as qs
from src.strategies.base_strategy import BaseStrategy
from src.utils.logger import logger

class BacktestEngine:
    def __init__(self, strategy: BaseStrategy, data: pd.DataFrame):
        self.strategy = strategy
        self.data = data
        self.results = None

    def run(self, initial_cash=10000, fees=0.001, slippage=0.001):
        logger.info(f"Running backtest for {self.strategy.name}")

        # Generate signals
        signals = self.strategy.generate_signals(self.data)

        # VectorBT Portfolio
        portfolio = vbt.Portfolio.from_signals(
            self.data['close'],
            entries=(signals == 1),
            exits=(signals == -1),
            init_cash=initial_cash,
            fees=fees,
            slippage=slippage,
            freq='D'
        )
        self.results = portfolio
        return portfolio

    def get_metrics(self):
        if self.results is None:
            return {}

        returns = self.results.returns()
        metrics = {
            "Total Return": f"{self.results.total_return() * 100:.2f}%",
            "Sharpe Ratio": f"{self.results.sharpe_ratio():.2f}",
            "Max Drawdown": f"{self.results.max_drawdown() * 100:.2f}%",
            "Win Rate": f"{self.results.positions.win_rate() * 100:.2f}%" if hasattr(self.results.positions, 'win_rate') else "N/A",
            "Volatility": f"{returns.std() * np.sqrt(252) * 100:.2f}%"
        }
        return metrics

    def generate_report(self, output_path="report.html"):
        if self.results is None:
            return
        returns = self.results.returns()
        qs.reports.html(returns, output=output_path, title=f"Backtest Report - {self.strategy.name}")

    def run_monte_carlo(self, n_sims=50, n_days=252):
        """
        Simple Monte Carlo simulation based on historical returns
        """
        returns = self.data['close'].pct_change().dropna()
        if returns.empty:
            return None

        mu = returns.mean()
        sigma = returns.std()

        last_price = self.data['close'].iloc[-1]
        simulations = np.zeros((n_days, n_sims))

        for i in range(n_sims):
            daily_returns = np.random.normal(mu, sigma, n_days)
            price_path = last_price * (1 + daily_returns).accumulate()
            simulations[:, i] = price_path

        return simulations

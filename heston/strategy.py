import numpy as np
import pandas as pd
from .model import HestonModel

class HestonTradingStrategy:
    def __init__(self, model: HestonModel):
        """
        Initialize the trading strategy with a Heston model.
        """
        self.model = model

    def evaluate_opportunities(self, options_data):
        """
        Evaluate trading opportunities based on market data.

        Parameters:
        options_data (pd.DataFrame): DataFrame containing 'strike', 'expiry', 'market_price', 'type'

        Returns:
        pd.DataFrame: Original data with 'heston_price' and 'signal' added.
        """
        signals = []
        heston_prices = []

        for index, row in options_data.iterrows():
            k = row['strike']
            t = row['expiry']
            opt_type = row['type']
            market_price = row['market_price']

            # Calculate theoretical price using Heston model
            heston_price = self.model.price_european_option(k, t, opt_type)
            heston_prices.append(heston_price)

            # Simple signal: buy if undervalued, sell if overvalued
            # threshold of 1% to avoid overtrading
            if heston_price > market_price * 1.01:
                signals.append('BUY')
            elif heston_price < market_price * 0.99:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        options_data['heston_price'] = heston_prices
        options_data['signal'] = signals

        return options_data

    def backtest_strategy(self, S_paths, V_paths, K, T, option_type='call'):
        """
        A very simplified backtest showing the potential profit of buying an option
        at t=0 if the Heston model says it's undervalued compared to a Black-Scholes market.

        This is mostly for demonstration purposes.
        """
        # Assume market price is some value (e.g., Black-Scholes price with constant vol)
        # For simplicity, let's just use the average terminal payoff from simulation
        terminal_payoff = np.maximum(S_paths[-1] - K, 0) if option_type == 'call' else np.maximum(K - S_paths[-1], 0)
        expected_payoff = np.exp(-self.model.r * T) * np.mean(terminal_payoff)

        heston_price = self.model.price_european_option(K, T, option_type)

        return {
            'heston_price': heston_price,
            'simulated_fair_value': expected_payoff,
            'difference': abs(heston_price - expected_payoff)
        }

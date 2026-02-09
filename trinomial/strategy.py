import pandas as pd
from .model import TrinomialTreeModel

class TrinomialTradingStrategy:
    def __init__(self, model: TrinomialTreeModel, n_steps=100):
        """
        Initialize the trading strategy with a Trinomial Tree model.

        Parameters:
        model (TrinomialTreeModel): The pricing model
        n_steps (int): Number of steps to use in the tree for pricing
        """
        self.model = model
        self.n_steps = n_steps

    def evaluate_opportunities(self, options_data):
        """
        Evaluate trading opportunities based on market data.

        Parameters:
        options_data (pd.DataFrame): DataFrame containing 'strike', 'expiry', 'market_price', 'type', 'style'

        Returns:
        pd.DataFrame: Original data with 'trinomial_price' and 'signal' added.
        """
        trinomial_prices = []
        signals = []

        for index, row in options_data.iterrows():
            k = row['strike']
            t = row['expiry']
            opt_type = row['type']
            opt_style = row.get('style', 'european')
            market_price = row['market_price']

            # Calculate theoretical price using Trinomial model
            price = self.model.price_option(k, t, self.n_steps, opt_type, opt_style)
            trinomial_prices.append(price)

            # Simple signal: buy if undervalued, sell if overvalued
            # threshold of 1% to avoid overtrading
            if price > market_price * 1.01:
                signals.append('BUY')
            elif price < market_price * 0.99:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        options_data['trinomial_price'] = trinomial_prices
        options_data['signal'] = signals

        return options_data

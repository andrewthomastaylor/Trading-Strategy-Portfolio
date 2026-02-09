import pandas as pd
from .model import BinomialModel

class BinomialTradingStrategy:
    def __init__(self, model: BinomialModel, N=100):
        """
        Initialize the trading strategy with a Binomial model.

        Parameters:
        model (BinomialModel): An instance of the BinomialModel class
        N (int): Number of steps to use in the binomial tree for pricing
        """
        self.model = model
        self.N = N

    def evaluate_opportunities(self, options_data):
        """
        Evaluate trading opportunities based on market data.

        Parameters:
        options_data (pd.DataFrame): DataFrame containing 'strike', 'expiry', 'market_price', 'type',
                                     and optionally 'exercise_style'.

        Returns:
        pd.DataFrame: Original data with 'binomial_price' and 'signal' added.
        """
        signals = []
        binomial_prices = []

        for index, row in options_data.iterrows():
            k = row['strike']
            t = row['expiry']
            opt_type = row['type']
            # Default to European if style is not specified
            style = row.get('exercise_style', 'european')
            market_price = row['market_price']

            # Calculate theoretical price using Binomial model
            price = self.model.price_option(k, t, self.N, opt_type, style)
            binomial_prices.append(price)

            # Simple signal: buy if undervalued, sell if overvalued
            # threshold of 1% to avoid overtrading
            if price > market_price * 1.01:
                signals.append('BUY')
            elif price < market_price * 0.99:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        options_data['binomial_price'] = binomial_prices
        options_data['signal'] = signals

        return options_data

import pandas as pd
from .model import FiniteDifferenceModel

class FDMTradingStrategy:
    def __init__(self, model: FiniteDifferenceModel):
        """
        Initialize the trading strategy with an FDM model.
        """
        self.model = model

    def evaluate_opportunities(self, options_data, s0, r, sigma):
        """
        Evaluate trading opportunities based on market data.

        Parameters:
        options_data (pd.DataFrame): DataFrame containing 'strike', 'expiry', 'market_price', 'type', 'exercise_style'
        s0 (float): Current stock price
        r (float): Risk-free rate
        sigma (float): Volatility

        Returns:
        pd.DataFrame: Original data with 'fdm_price' and 'signal' added.
        """
        fdm_prices = []
        signals = []

        for index, row in options_data.iterrows():
            k = row['strike']
            t = row['expiry']
            opt_type = row['type']
            exercise = row.get('exercise_style', 'european')
            market_price = row['market_price']

            # Calculate theoretical price using FDM model
            fdm_price = self.model.price_option(s0, k, t, r, sigma, opt_type, exercise)
            fdm_prices.append(fdm_price)

            # Simple signal: buy if undervalued, sell if overvalued
            if fdm_price > market_price * 1.01:
                signals.append('BUY')
            elif fdm_price < market_price * 0.99:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        options_data['fdm_price'] = fdm_prices
        options_data['signal'] = signals

        return options_data

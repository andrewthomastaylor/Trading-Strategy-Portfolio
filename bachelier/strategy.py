import pandas as pd
import numpy as np
from .model import BachelierModel

class BachelierTradingStrategy:
    def __init__(self, model: BachelierModel):
        """
        Initialize the strategy with a Bachelier model.
        """
        self.model = model

    def evaluate_opportunities(self, options_data: pd.DataFrame):
        """
        Evaluate trading opportunities based on market data.

        Parameters:
        options_data (pd.DataFrame): DataFrame with columns 'strike', 'expiry', 'market_price', 'type'

        Returns:
        pd.DataFrame: DataFrame with added 'bachelier_price' and 'signal'
        """
        theo_prices = []
        signals = []

        for index, row in options_data.iterrows():
            k = row['strike']
            t = row['expiry']
            opt_type = row['type']
            market_price = row['market_price']

            # Calculate theoretical price
            theo_price = self.model.price_european_option(k, t, opt_type)
            theo_prices.append(theo_price)

            # Signal: Buy if undervalued by 5%, Sell if overvalued by 5%
            if theo_price > market_price * 1.05:
                signals.append('BUY')
            elif theo_price < market_price * 0.95:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        options_data = options_data.copy()
        options_data['bachelier_price'] = theo_prices
        options_data['signal'] = signals

        return options_data

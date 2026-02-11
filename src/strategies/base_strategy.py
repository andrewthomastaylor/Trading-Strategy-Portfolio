from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, name, params=None):
        self.name = name
        self.params = params or {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame):
        """
        Generate buy/sell signals based on input data.
        Returns a Series or DataFrame with signals.
        """
        pass

    @abstractmethod
    def get_indicators(self, data: pd.DataFrame):
        """
        Calculate and return indicators used by the strategy.
        """
        pass

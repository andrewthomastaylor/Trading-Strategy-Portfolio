import pandas as pd

class BaseStrategy:
    def __init__(self, name="BaseStrategy", params=None):
        self.name = name
        self.params = params or {}
        self.logic_trace = []

    def generate_signals(self, data: pd.DataFrame, fundamentals: dict = None) -> pd.Series:
        """
        Returns a series of signals: 1 (Buy), -1 (Sell), 0 (Hold)
        """
        raise NotImplementedError("Subclasses must implement generate_signals")

import pytest
import pandas as pd
import numpy as np
from src.api.data_provider import DataProvider
from src.api.alpaca_wrapper import AlpacaClient

def test_data_provider_yfinance():
    provider = DataProvider()
    # Use a well-known symbol that should have data
    from alpaca.data.timeframe import TimeFrame
    from datetime import datetime, timedelta

    end = datetime.now()
    start = end - timedelta(days=5)

    data = provider.fetch_data("AAPL", TimeFrame.Day, start, end, source="yfinance")
    # In tests, might be empty if no internet, but we check if it handles it
    assert isinstance(data, pd.DataFrame)
    if not data.empty:
        assert 'close' in data.columns

def test_data_provider_extended():
    provider = DataProvider()
    from alpaca.data.timeframe import TimeFrame
    data = provider.fetch_extended_data("MSFT", TimeFrame.Day, years=1)
    assert isinstance(data, pd.DataFrame)

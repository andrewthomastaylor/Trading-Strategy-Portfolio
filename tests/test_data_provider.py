from src.api.data_provider import DataProvider
from src.api.alpaca_wrapper import AlpacaClient
from unittest.mock import MagicMock
import pandas as pd

def test_data_provider():
    mock_client = MagicMock(spec=AlpacaClient)
    mock_client.get_historical_bars.return_value = pd.DataFrame({'close': [100]}, index=[pd.Timestamp.now()])

    provider = DataProvider(mock_client)
    data = provider.get_historical_data("AAPL", "1Day", start="2023-01-01")

    assert not data.empty
    print("DataProvider test passed.")

if __name__ == "__main__":
    test_data_provider()

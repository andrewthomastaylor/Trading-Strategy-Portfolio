import pytest
from src.api.alpaca_wrapper import AlpacaClient

def test_alpaca_client_init():
    client = AlpacaClient(api_key="test", secret_key="test")
    assert client.api_key == "test"
    assert client.secret_key == "test"
    assert client.paper == True

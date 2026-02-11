from src.monitoring.live_monitor import LiveMonitor
from src.api.alpaca_wrapper import AlpacaClient
from src.utils.database import Database
import streamlit as st

_monitor_instance = None

def get_monitor(db: Database):
    global _monitor_instance
    if _monitor_instance is None:
        api_key = db.get_settings("alpaca_api_key")
        api_secret = db.get_settings("alpaca_api_secret")
        paper = db.get_settings("alpaca_paper") == "True"

        if api_key and api_secret:
            client = AlpacaClient(api_key, api_secret, paper)
            _monitor_instance = LiveMonitor(client, db)
    return _monitor_instance

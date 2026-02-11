import threading
import time
import pandas as pd
from datetime import datetime
from src.api.alpaca_wrapper import AlpacaClient
from src.api.data_provider import DataProvider
from src.strategies.indicator_strategy import IndicatorStrategy
from src.utils.logger import logger
from src.utils.database import Database

class LiveMonitor:
    def __init__(self, alpaca_client: AlpacaClient, db: Database):
        self.alpaca = alpaca_client
        self.data_provider = DataProvider(alpaca_client)
        self.db = db
        self.running = False
        self.thread = None
        self.interval = 60 # Default 1 minute
        self.symbols = []
        self.strategy = None

    def start(self, symbols, timeframe, strategy_params):
        if self.running:
            return

        self.symbols = symbols
        self.strategy = IndicatorStrategy("Live Strategy", strategy_params)
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, args=(timeframe,), daemon=True)
        self.thread.start()
        logger.info(f"Live monitoring started for {symbols}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Live monitoring stopped")

    def _monitor_loop(self, timeframe):
        while self.running:
            try:
                # Check market hours
                clock = self.alpaca.get_clock()
                if not clock.is_open:
                    logger.info("Market is closed. Waiting...")
                    time.sleep(300)
                    continue

                for symbol in self.symbols:
                    # Fetch recent data
                    df = self.data_provider.get_historical_data(symbol, timeframe, limit=100)
                    if df.empty:
                        continue

                    # Generate signal
                    signals = self.strategy.generate_signals(df)
                    last_signal = signals.iloc[-1]

                    if last_signal != 0:
                        self._handle_signal(symbol, last_signal)

                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(60)

    def _handle_signal(self, symbol, signal):
        side = "buy" if signal == 1 else "sell"
        logger.info(f"SIGNAL: {side.upper()} {symbol}")

        # Log to DB
        self.db.log_trade(symbol, side, 0.0, 0.0, f"Strategy signal {side}")

        # Place order if in live/paper mode (logic can be expanded here)
        # self.alpaca.place_order(symbol, qty=1, side=side)

import threading
import time
import schedule
from datetime import datetime
from src.api.alpaca_wrapper import AlpacaClient
from src.utils.logger import logger
from src.notifications.email_service import EmailService

class LiveMonitor:
    def __init__(self, alpaca_client: AlpacaClient, email_service: EmailService = None):
        self.alpaca_client = alpaca_client
        self.email_service = email_service
        self.running = False
        self.thread = None
        self.strategies = []
        self.symbols = []
        self.interval_minutes = 1
        self.trade_history = [] # To store logs of trades with reasons

    def add_strategy(self, strategy, symbols):
        self.strategies.append(strategy)
        self.symbols.extend(symbols)
        self.symbols = list(set(self.symbols)) # Unique symbols

    def start(self, interval_minutes=1):
        if self.running:
            logger.warning("Monitor is already running.")
            return

        self.interval_minutes = interval_minutes
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"Live monitor started with {interval_minutes} min interval.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Live monitor stopped.")

    def _run_loop(self):
        while self.running:
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Error in monitor tick: {e}")
                if self.email_service:
                    self.email_service.send_email("Trading App Error", f"Critical error in monitor loop: {e}")

            # Wait for next interval
            time.sleep(self.interval_minutes * 60)

    def _tick(self):
        logger.info(f"Monitor tick at {datetime.now()}")

        for symbol in self.symbols:
            # Fetch latest data (e.g., last 100 bars for indicators)
            from alpaca.data.timeframe import TimeFrame
            from datetime import timedelta

            end = datetime.now()
            start = end - timedelta(days=5) # Sufficient for most indicators on low timeframes

            data = self.alpaca_client.get_historical_bars(symbol, TimeFrame.Minute, start, end)
            if data.empty:
                continue

            for strategy in self.strategies:
                signals = strategy.generate_signals(data)
                last_signal = signals.iloc[-1]

                if last_signal != 0:
                    reason = f"Strategy {strategy.name} generated {last_signal} signal"
                    self._execute_trade(symbol, last_signal, reason)

    def _execute_trade(self, symbol, signal, reason=""):
        side = "buy" if signal == 1 else "sell"
        logger.info(f"Signal detected for {symbol}: {side}. Reason: {reason}")

        # In a real app, we'd check current positions and buying power
        # For this implementation, we'll place a small market order as a demo
        order = self.alpaca_client.place_market_order(symbol, qty=1, side=side)

        if order:
            msg = f"Executed {side} order for {symbol}"
            logger.info(msg)
            self.trade_history.append({
                "timestamp": datetime.now(),
                "symbol": symbol,
                "side": side,
                "reason": reason,
                "status": "success"
            })
            if self.email_service:
                self.email_service.send_email(f"Trade Executed: {symbol}", msg)
        else:
            self.trade_history.append({
                "timestamp": datetime.now(),
                "symbol": symbol,
                "side": side,
                "reason": reason,
                "status": "failed"
            })
            msg = f"Failed to execute {side} order for {symbol}"
            logger.error(msg)
            if self.email_service:
                self.email_service.send_email(f"Trade Failure: {symbol}", msg)

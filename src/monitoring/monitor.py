import threading
import time
import schedule
from datetime import datetime
from src.api.alpaca_wrapper import AlpacaClient
from src.api.data_provider import DataProvider
from src.optimization.optimizer import PortfolioOptimizer
from src.utils.logger import logger
from src.notifications.email_service import EmailService

class LiveMonitor:
    def __init__(self, alpaca_client: AlpacaClient, email_service: EmailService = None, db=None):
        self.alpaca_client = alpaca_client
        self.provider = DataProvider(alpaca_client)
        self.email_service = email_service
        self.db = db
        self.running = False
        self.thread = None
        self.strategies = []
        self.symbols = []
        self.interval_minutes = 1
        self.trade_history = [] # To store logs of trades with reasons
        self.latest_status = {} # To store latest indicator values and signals for UI
        self.reoptimize_interval = 0 # 0 means disabled
        self.tick_count = 0

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
                clock = self.alpaca_client.get_clock()
                if clock and not clock.is_open:
                    logger.info("Market is closed. Skipping tick.")
                    # Optional: send a one-time notification or log
                else:
                    self._tick()
            except Exception as e:
                logger.error(f"Error in monitor tick: {e}")
                if self.email_service:
                    self.email_service.send_email("Trading App Error", f"Critical error in monitor loop: {e}")

            # Wait for next interval
            time.sleep(self.interval_minutes * 60)

    def _tick(self):
        logger.info(f"Monitor tick at {datetime.now()}")
        self.tick_count += 1

        # Dynamic Re-optimization
        if self.reoptimize_interval > 0 and self.tick_count % self.reoptimize_interval == 0:
            self._reoptimize_portfolio()

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
                fundamentals = self.provider.fetch_fundamentals(symbol)
                signals = strategy.generate_signals(data, fundamentals=fundamentals)
                last_signal = signals.iloc[-1]

                # Update status for UI
                self.latest_status[symbol] = {
                    "timestamp": datetime.now(),
                    "signal": last_signal,
                    "indicators": strategy.get_indicators(data).iloc[-1].to_dict()
                }

                if last_signal != 0:
                    reason = f"Strategy {strategy.name} generated {last_signal} signal"
                    self._execute_trade(symbol, last_signal, reason)

    def _reoptimize_portfolio(self):
        logger.info("Running dynamic portfolio re-optimization...")
        try:
            from alpaca.data.timeframe import TimeFrame
            import pandas as pd
            from datetime import timedelta

            end = datetime.now()
            start = end - timedelta(days=365)

            price_data = {}
            for sym in self.symbols:
                df = self.provider.fetch_data(sym, TimeFrame.Day, start, end, source="yfinance")
                if not df.empty:
                    price_data[sym] = df['close']

            if not price_data: return

            combined_df = pd.DataFrame(price_data).dropna()
            if combined_df.empty: return

            optimizer = PortfolioOptimizer(combined_df)
            weights = optimizer.optimize_weights()

            if weights:
                logger.info(f"New optimized weights: {weights}")
                if self.email_service:
                    self.email_service.send_email("Portfolio Re-optimized", f"New weights: {weights}")
                # In a full implementation, we would adjust positions to match these weights
        except Exception as e:
            logger.error(f"Error in dynamic re-optimization: {e}")

    def _execute_trade(self, symbol, signal, reason=""):
        side = "buy" if signal == 1 else "sell"
        logger.info(f"Signal detected for {symbol}: {side}. Reason: {reason}")

        # Calculate quantity based on buying power / equity
        try:
            account = self.alpaca_client.get_account()
            if not account:
                logger.error("Could not fetch account for trade execution.")
                return

            equity = float(account.equity)
            allocation_pct = 0.05 # Use 5% of equity per trade
            trade_value = equity * allocation_pct

            # Fetch latest price to estimate qty
            end = datetime.now()
            start = end - timedelta(minutes=5)
            from alpaca.data.timeframe import TimeFrame
            price_data = self.alpaca_client.get_historical_bars(symbol, TimeFrame.Minute, start, end)
            if price_data.empty:
                logger.warning(f"Could not fetch price for {symbol}. Defaulting to qty=1")
                qty = 1
            else:
                last_price = price_data['close'].iloc[-1]
                qty = int(trade_value / last_price)
                if qty < 1: qty = 1
        except Exception as e:
            logger.error(f"Error calculating trade qty: {e}. Defaulting to 1.")
            qty = 1

        order = self.alpaca_client.place_market_order(symbol, qty=qty, side=side)

        if order:
            msg = f"Executed {side} order for {symbol}"
            logger.info(msg)
            trade_entry = {
                "timestamp": datetime.now(),
                "symbol": symbol,
                "side": side,
                "reason": reason,
                "status": "success"
            }
            self.trade_history.append(trade_entry)
            if self.db:
                self.db.save_trade(symbol, side, reason, "success")
            if self.email_service:
                self.email_service.send_email(f"Trade Executed: {symbol}", msg)
        else:
            trade_entry = {
                "timestamp": datetime.now(),
                "symbol": symbol,
                "side": side,
                "reason": reason,
                "status": "failed"
            }
            self.trade_history.append(trade_entry)
            if self.db:
                self.db.save_trade(symbol, side, reason, "failed")
            msg = f"Failed to execute {side} order for {symbol}"
            logger.error(msg)
            if self.email_service:
                self.email_service.send_email(f"Trade Failure: {symbol}", msg)

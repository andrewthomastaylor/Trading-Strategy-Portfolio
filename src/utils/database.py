import sqlite3
import json
from datetime import datetime
from src.utils.logger import logger

class Database:
    def __init__(self, db_path="trading.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Trade logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        symbol TEXT,
                        side TEXT,
                        reason TEXT,
                        status TEXT
                    )
                """)

                # Settings table (key-value)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)

                # Strategies table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS strategies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        params TEXT,
                        is_active INTEGER DEFAULT 0
                    )
                """)

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def save_trade(self, symbol, side, reason, status):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO trades (timestamp, symbol, side, reason, status) VALUES (?, ?, ?, ?, ?)",
                    (datetime.now(), symbol, side, reason, status)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving trade to DB: {e}")

    def get_trades(self, limit=100):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching trades from DB: {e}")
            return []

    def set_setting(self, key, value):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, json.dumps(value))
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving setting {key} to DB: {e}")

    def get_setting(self, key, default=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                return json.loads(row[0]) if row else default
        except Exception as e:
            logger.error(f"Error fetching setting {key} from DB: {e}")
            return default

    def save_strategy(self, name, params, is_active=0):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO strategies (name, params, is_active) VALUES (?, ?, ?)",
                    (name, json.dumps(params), is_active)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving strategy to DB: {e}")

    def get_strategies(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM strategies")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching strategies from DB: {e}")
            return []

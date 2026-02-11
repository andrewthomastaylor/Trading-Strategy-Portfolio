import sqlite3
import json
import os
from datetime import datetime
from src.utils.logger import logger

class Database:
    def __init__(self, db_path="data/trading.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            # Trades history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    side TEXT,
                    qty REAL,
                    price REAL,
                    reason TEXT
                )
            ''')
            # Strategies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategies (
                    name TEXT PRIMARY KEY,
                    params TEXT
                )
            ''')
            conn.commit()

    def save_setting(self, key, value):
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
            conn.commit()

    def get_settings(self, key, default=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                val = row[0]
                try:
                    # If it's a JSON string, load it. If not, return as is.
                    return json.loads(val)
                except:
                    return val
            return default

    def log_trade(self, symbol, side, qty, price, reason):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO trades (timestamp, symbol, side, qty, price, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), symbol, side, qty, price, reason))
            conn.commit()

    def get_trades(self, limit=100):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?', (limit,))
            return cursor.fetchall() # UI expects list of tuples or rows

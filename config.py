import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Alpaca API Configuration
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "your_api_key_here")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "your_secret_key_here")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password_here")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "your_email@gmail.com")

# Trading Settings
SYMBOL = os.getenv("SYMBOL", "SPY")
QUANTITY = int(os.getenv("QUANTITY", 10))

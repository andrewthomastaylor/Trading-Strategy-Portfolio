import logging
import sys
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("trading_app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler - but we'll avoid committing the actual log file
fh = logging.FileHandler("logs/trading.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

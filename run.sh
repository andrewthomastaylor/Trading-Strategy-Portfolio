#!/bin/bash

echo "Starting Alpaca Algo Trader..."

# Check if .env exists
if [ ! -f .env ]; then
    echo ".env file not found. Creating from template..."
    cp .env.template .env
    echo "Please edit .env with your Alpaca API keys and Email credentials."
fi

# Install dependencies if needed
# pip install -r requirements.txt

# Run Streamlit
export PYTHONPATH=.
streamlit run app.py

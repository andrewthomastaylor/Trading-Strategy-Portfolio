@echo off
echo Starting Alpaca Algo Trader...

if not exist .env (
    echo .env file not found. Creating from template...
    copy .env.template .env
    echo Please edit .env with your Alpaca API keys and Email credentials.
)

set PYTHONPATH=.
streamlit run app.py
pause

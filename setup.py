import os
import shutil
import subprocess
import sys

def setup():
    print("Setting up the Modular Trading System...")

    # 1. Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Error installing dependencies: {e}")

    # 2. Create .env if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating .env from example...")
        shutil.copy(".env.example", ".env")
        print("Please edit .env with your API keys.")
    else:
        print(".env already exists.")

    # 3. Create .gitignore if it doesn't exist
    if not os.path.exists(".gitignore"):
        print("Creating .gitignore...")
        with open(".gitignore", "w") as f:
            f.write(".env\n__pycache__/\n*.pyc\nreport_*.html\n")

    print("\nSetup complete!")
    print("Next steps:")
    print("1. Edit .env with your credentials.")
    print("2. Run a backtest: python backtester.py")
    print("3. Run live trader: python live_trader.py --run-once")

if __name__ == "__main__":
    setup()

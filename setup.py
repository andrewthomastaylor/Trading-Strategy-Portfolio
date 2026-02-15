import os
import shutil
import subprocess
import sys

def setup():
    print("Setting up the Algorithmic Trading System...")

    # 1. Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Error installing dependencies: {e}")

    # 2. Create config.py if it doesn't exist
    if not os.path.exists("config.py"):
        print("Creating config.py from template...")
        shutil.copy("config_template.py", "config.py")
        print("Please edit config.py with your API keys.")
    else:
        print("config.py already exists.")

    # 3. Create .gitignore if it doesn't exist
    if not os.path.exists(".gitignore"):
        print("Creating .gitignore...")
        with open(".gitignore", "w") as f:
            f.write("config.py\n__pycache__/\n*.pyc\nreport_*.html\n.env\n")

    print("\nSetup complete!")
    print("Next steps:")
    print("1. Edit config.py with your Alpaca API credentials.")
    print("2. Run a backtest: python backtester.py")
    print("3. Run live trader once: python live_trader.py --run-once")

if __name__ == "__main__":
    setup()

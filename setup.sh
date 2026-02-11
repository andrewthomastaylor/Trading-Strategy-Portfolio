#!/bin/bash
echo "Starting setup..."

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Please install Python 3."
    exit
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from .env.example if .env doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Setup complete! You can now run the models."
echo "To activate the environment, run: source venv/bin/activate"

# Options Trading Models

This repository contains implementations of various options trading models and strategies, including Heston and Bachelier models.

## Project Structure

- `heston/`: Heston Stochastic Volatility Model implementation.
- `bachelier/`: Bachelier (Normal) Model implementation.
- `tests/`: Unit tests for the models and strategies.
- `main.py`: Example usage of the Heston model.
- `demo_bachelier.py`: Example usage of the Bachelier model.

## Setup

We have provided automated setup scripts to handle dependency installation and environment configuration.

### Windows
1. Double-click `setup.bat`.
2. This will create a virtual environment, install all required dependencies from `requirements.txt`, and set up your `.env` file.

### Linux / macOS
1. Open your terminal.
2. Run `./setup.sh`.
3. This will create a virtual environment, install all required dependencies, and set up your `.env` file.

## Running the Models

After setup, you can run the demonstration scripts:

### Heston Model
```bash
PYTHONPATH=. python main.py
```

### Bachelier Model
```bash
PYTHONPATH=. python demo_bachelier.py
```

## Testing

To run the tests, use:

```bash
PYTHONPATH=. python -m pytest
```

## Configuration

Environment-specific settings can be adjusted in the `.env` file created during setup.

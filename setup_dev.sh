#!/bin/bash
# Setup script for IsoTalia development environment

echo "Setting up IsoTalia development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version detected"
else
    echo "✗ Python 3.8+ required, found $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "Installing development dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run initial code quality checks
echo "Running initial code quality checks..."
echo "Running Black formatter..."
black --check . || black .

echo "Running Ruff linter..."
ruff check . || ruff check --fix .

echo "Running tests..."
python -m pytest tests/ -v

echo ""
echo "✓ Development environment setup complete!"
echo ""
echo "To activate the environment in future sessions:"
echo "  source venv/bin/activate"
echo ""
echo "To run the game:"
echo "  python main.py"
echo ""
echo "To run tests with coverage:"
echo "  pytest --cov=core --cov=rendering --cov-report=html"
echo ""
echo "To format code:"
echo "  black ."
echo "  ruff check --fix ."
echo ""
echo "To run pre-commit on all files:"
echo "  pre-commit run --all-files"
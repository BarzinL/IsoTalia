#!/bin/bash
# IsoTalia Development Environment Setup Script
# This script sets up a complete development environment for IsoTalia

set -e  # Exit on any error

echo "🚀 IsoTalia Development Environment Setup"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "📋 Detected Python version: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8+ required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "🎮 Installing IsoTalia in development mode..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  Pre-commit not available - skipping hook installation"
fi

# Run initial tests to verify setup
echo "🧪 Running initial test suite..."
if python -m pytest tests/unit/test_events.py -v --tb=short; then
    echo "✅ Test suite passed - development environment ready!"
else
    echo "⚠️  Some tests failed - check output above"
fi

# Show next steps
echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📚 Next steps:"
echo "  • Run the game: python main.py"
echo "  • Run all tests: pytest"
echo "  • Check code quality: pre-commit run --all-files"
echo "  • View development guide: cat docs/DEVELOPMENT.md"
echo ""
echo "💡 Useful commands:"
echo "  • Format code: black ."
echo "  • Check linting: ruff check ."
echo "  • Run coverage: pytest --cov=core --cov-report=html"
echo ""
echo "Happy coding! 🚀"
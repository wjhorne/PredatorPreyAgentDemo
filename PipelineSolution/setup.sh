#!/bin/bash
# Setup script for PipelineSolution
# Run this once to set up the pipeline: ./setup.sh

set -e

echo "Setting up PipelineSolution..."

# Check Python version (3.10+ required: mcp needs >=3.10; numpy 1.26 / matplotlib 3.8 need >=3.9)
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
echo "Python version: $python_version"

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    echo "Error: Python 3.10+ required (mcp needs >=3.10; numpy/matplotlib need >=3.9)"
    exit 1
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null

# Verify imports
echo "Verifying imports..."
python test_imports.py

# Run tests
echo "Running tests..."
python -m unittest tests.test_core -q

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next, try:"
echo "  ./query.sh 'How many rabbits at step 50?'"
echo "  ./query.sh 'Generate a PDF report' --output report.pdf"
echo ""

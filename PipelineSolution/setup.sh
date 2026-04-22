#!/bin/bash
# Setup script for PipelineSolution
# Run this once to set up the pipeline: ./setup.sh

set -e

echo "Setting up PipelineSolution..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python version: $python_version"

if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "Error: Python 3.8+ required"
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

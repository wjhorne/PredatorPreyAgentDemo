#!/bin/bash
# Query wrapper for PipelineSolution
# Usage: ./query.sh "How many foxes at step 180?"
#        ./query.sh "Generate a report" --format pdf --output report.pdf

if [ -z "$1" ]; then
    echo "Usage: $0 <query> [options]"
    echo ""
    echo "Examples:"
    echo "  $0 'How many rabbits at step 50?'"
    echo "  $0 'Show me foxes and rabbits' --format pdf"
    echo "  $0 'Simulate with nx=40, ny=40' --format text"
    echo "  $0 '50x50 grid, 200 steps' --validate"
    echo ""
    echo "Options:"
    echo "  --format {text,pdf}    Output format (default: text)"
    echo "  --output FILE          Save to file instead of stdout"
    echo "  --validate             Validate against example baseline"
    echo ""
    exit 1
fi

# Activate venv if needed
if [ ! -z "$VIRTUAL_ENV" ]; then
    # Already in venv
    :
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Run './setup.sh' first."
    exit 1
fi

# Extract the query (first argument) and remaining options
QUERY="$1"
shift

# Run pipeline with --query flag
python pipeline.py --query "$QUERY" "$@"

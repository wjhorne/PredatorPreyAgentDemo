#!/bin/bash
# Integration test for PipelineSolution
# This script verifies that the pipeline works end-to-end for AI tool usage

echo "======================================"
echo "PipelineSolution Integration Test"
echo "======================================"
echo ""

# Check if venv is set up
if [ ! -f ".venv/bin/activate" ]; then
    echo "✗ Virtual environment not found. Run './setup.sh' first."
    exit 1
fi

source .venv/bin/activate

# Test 1: Query for rabbit population
echo "Test 1: Query for rabbit population at step 50..."
output=$(python pipeline.py --query "How many rabbits at step 50?" --format text 2>&1)
if echo "$output" | grep -q "Population at step 50"; then
    echo "✓ Rabbit query successful"
else
    echo "✗ Rabbit query failed"
    exit 1
fi

# Test 2: Query for fox population  
echo "Test 2: Query for fox population at step 100..."
output=$(python pipeline.py --query "How many foxes at step 100?" --format text 2>&1)
if echo "$output" | grep -q "Population at step 100"; then
    echo "✓ Fox query successful"
else
    echo "✗ Fox query failed"
    exit 1
fi

# Test 3: Parameter override (different grid size)
echo "Test 3: Parameter override (40x40 grid)..."
output=$(python pipeline.py --query "40x40 grid, rabbits at step 50" --format text 2>&1)
if echo "$output" | grep -q "Grid size:              40 × 40"; then
    echo "✓ Parameter override successful"
else
    echo "✗ Parameter override failed"
    exit 1
fi

# Test 4: PDF generation
echo "Test 4: PDF generation..."
rm -f test_integration.pdf
python pipeline.py --query "Generate report" --format pdf --output test_integration.pdf 2>&1 > /dev/null
if [ -f "test_integration.pdf" ] && [ -s "test_integration.pdf" ]; then
    echo "✓ PDF generation successful"
    rm -f test_integration.pdf
else
    echo "✗ PDF generation failed"
    exit 1
fi

# Test 5: Baseline validation
echo "Test 5: Baseline validation..."
output=$(python pipeline.py --query "50x50 grid, 360 steps, seed 12345" --format text --validate 2>&1)
if echo "$output" | grep -q "Status: PASSED"; then
    echo "✓ Baseline validation passed"
else
    echo "✗ Baseline validation failed"
    exit 1
fi

# Test 6: Using query wrapper script
echo "Test 6: Query wrapper script..."
output=$(bash query.sh "How many foxes at step 180?" 2>&1)
if echo "$output" | grep -q "Population at step 180"; then
    echo "✓ Query wrapper successful"
else
    echo "✗ Query wrapper failed"
    exit 1
fi

echo ""
echo "======================================"
echo "✓ All tests passed!"
echo "======================================"
echo ""
echo "The system is ready for AI tool usage."
echo "Try:"
echo "  ./query.sh 'How many rabbits at step 50?'"
echo "  ./query.sh 'Generate a PDF report' --output report.pdf"
echo ""

# AI-Friendly Setup: PipelineSolution

## ⭐ Important: Use MCP for Best Results

**If you're using Claude Code, Cursor, or VS Code with Claude extension:**
→ Use **MCP Tools** instead of the query wrapper
→ Read [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for setup

**Benefits of MCP:**
- Type-safe parameter definitions
- Full IDE integration
- No manual parsing needed
- LLM can see exactly what's available

---

## Summary

The PipelineSolution is now fully configured for use by AI assistants (Claude Code, Gemini, Copilot, Codex, etc.).

## What Was Added

### 1. **setup.sh** (Automated Setup)
- One-command setup: `./setup.sh`
- Creates virtual environment
- Installs all dependencies
- Verifies imports and runs tests
- AI tools can simply invoke this to initialize

### 2. **query.sh** (Simple Query Wrapper)
- Wraps the Python pipeline.py with simpler invocation
- Usage: `./query.sh "How many foxes at step 180?"`
- AI tools can easily call this without knowing Python CLI syntax
- Handles venv activation automatically

### 3. **.instructions.md** (AI Instructions)
- Explicit documentation for AI assistants
- Clear examples of what to ask for
- Examples of how to interpret results
- Usage patterns and troubleshooting

### 4. **QUICKSTART.txt** (Quick Reference)
- One-page setup and usage guide
- Easy for AI tools to scan
- Common query examples
- Default parameters listed

### 5. **test_integration.sh** (End-to-End Tests)
- 6 integration tests verify everything works
- Tests queries, parameter overrides, PDF generation, validation
- All pass ✓

## How It Works for AI Tools

### Scenario 1: Gemini Code
```
User: "Open PipelineSolution in Gemini Code and ask it how many foxes are at step 180"

1. Gemini opens PipelineSolution folder
2. Gemini reads QUICKSTART.txt and .instructions.md
3. Gemini runs: ./setup.sh
4. Gemini runs: ./query.sh "How many foxes at step 180?"
5. Gemini parses output and reports: "At step 180, there are 1530.37 foxes."
```

### Scenario 2: Claude Code
```
User: "Generate a PDF report of a 40x40 simulation"

1. Claude reads the instructions
2. Claude runs: ./query.sh "40x40 grid" --format pdf --output report.pdf
3. Claude confirms: "✓ PDF report generated: report.pdf"
```

### Scenario 3: Codex/Copilot
```
User: "What's the difference between rabbits and foxes at step 100 with different seeds?"

1. Codex runs: ./query.sh "100 steps, seed 999" --format text
2. Codex parses and compares with another run
3. Codex presents the analysis
```

## Files Structure for AI Tools

```
PipelineSolution/
├── QUICKSTART.txt          ← Read this first (quick reference)
├── .instructions.md        ← Read this for details
├── README.md               ← Full documentation
├── setup.sh               ← Run this to initialize
├── query.sh               ← Run this to query
├── test_integration.sh    ← Run this to verify setup
├── pipeline.py            ← Main Python entry point
├── query_engine.py        ← Plain language parser
├── config_builder.py      ← Config creation
├── simulation_runner.py   ← Runs simulations
├── report_generator.py    ← Creates reports
├── validation.py          ← Baseline validation
└── requirements.txt       ← Dependencies
```

## Verification

All 6 integration tests pass:
- ✓ Rabbit population queries
- ✓ Fox population queries
- ✓ Parameter overrides
- ✓ PDF generation
- ✓ Baseline validation
- ✓ Query wrapper script

## What an AI Tool Can Do

An AI tool with access to this folder can now:

1. **Answer population queries**: "How many rabbits at step X?"
2. **Generate reports**: "Create a PDF analysis"
3. **Run simulations**: "Simulate with nx=30, ny=30"
4. **Validate results**: "Verify against the baseline"
5. **Modify parameters**: "Use seed 999"
6. **Produce outputs**: Text summaries or PDF reports

## Example Interactions

### Example 1: Direct Query
```bash
$ ./query.sh "How many foxes at step 180?"
# Returns detailed text report with fox statistics
```

### Example 2: PDF Generation
```bash
$ ./query.sh "30x30 grid, 200 steps" --format pdf --output analysis.pdf
# Generates multi-page PDF with summary, time series, and spatial plots
```

### Example 3: Parameter Override
```bash
$ ./query.sh "40x40 grid, 400 steps, seed 999, show both"
# Runs simulation with custom parameters
```

### Example 4: Validation
```bash
$ ./query.sh "50x50 grid, 360 steps, seed 12345" --validate
# Validates against the hand-run baseline
```

## Key Features

✓ **One-step setup**: `./setup.sh`
✓ **Simple invocation**: `./query.sh "query"`
✓ **Natural language**: No syntax required
✓ **Deterministic**: Same seed = same results
✓ **Validated**: Against example_run baseline
✓ **Multiple outputs**: Text and PDF
✓ **Parameter control**: Fully customizable

## For AI Tools Reading This

If you're an AI assistant with access to this folder:

1. Read `QUICKSTART.txt` for immediate setup
2. Run `./setup.sh` (one time only)
3. Use `./query.sh "your question here"` for any query
4. Generate PDFs with `--format pdf --output filename.pdf`
5. Validate against baseline with `--validate`

You're now ready to answer any question about the predator-prey simulation!

# Simulation Analysis Pipeline

> **For AI Assistants (Claude Code, Gemini, etc.)**: 
> - **Recommended**: Use the MCP server for type-safe tool access → See [MCP_INTEGRATION.md](MCP_INTEGRATION.md)
> - **Alternative**: Use query wrapper for quick CLI access → See [.instructions.md](.instructions.md)

A query-driven pipeline that wraps the predator-prey simulation from `DevelopmentSolution/` to answer plain-language queries about rabbit and fox populations, and to generate analysis reports in text and PDF formats.

## Setup

### Prerequisites
- Python 3.8+
- Git (to clone the repo)

### Installation

1. Navigate to the PipelineSolution directory:
```bash
cd PipelineSolution
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation

Run the import test to confirm DevelopmentSolution modules are accessible:
```bash
python test_imports.py
```

Expected output:
```
✓ Imported SimulationConfig, run_simulation, validate
✓ Imported create_animation, render_animation
✓ Created test SimulationConfig: 10x10, 5 steps, seed 12345
✓ Ran micro simulation: returned arrays shape (10, 10, 5), (10, 10, 5)
  Final rabbit total: ..., final fox total: ...

✓ All imports and basic operations successful!
```

## Usage

### Query Examples

```bash
# Ask for rabbit population at a specific timestep
python pipeline.py --query "How many rabbits at step 50?" --format text

# Ask for both species
python pipeline.py --query "What are the rabbit and fox populations at step 100?"

# Request a full analysis report
python pipeline.py --query "Generate a report for the default simulation" --format pdf

# Override simulation parameters
python pipeline.py --query "Simulate with nx=40, ny=40 for 200 steps, then show foxes at step 150" --format text

# Validate against the golden baseline
python pipeline.py --query "Run the example configuration" --validate --format text
```

## Architecture

The pipeline follows a three-stage flow:

```
Query Input
    ↓
Parse & Validate
    ↓
Execute Simulation (imported from DevelopmentSolution)
    ↓
Optionally Validate Against Baseline
    ↓
Generate Report (Text or PDF)
    ↓
Output
```

### Key Components

- **pipeline.py**: CLI entry point and orchestrator
- **query_engine.py** (forthcoming): Plain-language query parser
- **config_builder.py** (forthcoming): Converts parsed queries to SimulationConfig
- **simulation_runner.py** (forthcoming): Executes simulations with caching
- **report_generator.py** (forthcoming): Generates text and PDF outputs
- **validation.py** (forthcoming): Validates results against example_run baseline

## Configuration

Default parameters are inherited from `DevelopmentSolution/example_run/INPUTS.md`:
- Grid size: 50×50
- Time steps: 360
- Seed: 12345
- Rabbit growth: 1.0
- Fox mortality: 0.72
- Diffusion rates: rabbit 0.01, fox 0.10
- Initial conditions: patch-based heterogeneity with patch_strength=0.80, patch_size=5

Override any parameter in a query using keywords like `nx=40`, `nt=200`, etc.

## Validation

The pipeline validates output against the hand-run baseline stored in `DevelopmentSolution/example_run/`:
- Parameters: as recorded in INPUTS.md
- Expected totals: from population_counts.csv

Run with `--validate` flag to check exact-match agreement within machine precision.

## Tests

(To be implemented) Unit and integration tests cover:
- Query parsing for various request patterns
- Config validation and error handling
- Exact-match baseline validation
- Text and PDF output generation
- CLI integration

Run tests with:
```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Project Structure

```
PipelineSolution/
├── README.md (this file)
├── requirements.txt
├── pipeline.py
├── query_engine.py
├── config_builder.py
├── simulation_runner.py
├── report_generator.py
├── validation.py
├── test_imports.py
├── tests/
│   ├── test_query_parser.py
│   ├── test_config_builder.py
│   ├── test_validation.py
│   └── test_end_to_end.py
├── baselines/
│   └── example_baseline.json
└── outputs/
    └── (generated reports and logs)
```

## Reproducibility

All simulations use deterministic seeds. To exactly reproduce a previous result:
1. Note the query and seed used (reported in output)
2. Re-run with the same query or explicitly pass `--seed <value>`

Example:
```bash
python pipeline.py --query "..." --seed 12345 --format pdf
```

The PDF and text outputs include instructions for exact reproducibility.

## Known Limitations

- Parser is keyword-based; complex natural language is simplified to common request patterns.
- PDF generation requires reportlab; plain-text output does not depend on it.
- Single-query model; no multi-turn agent dialogue or persistent state across runs.

## Future Work

- More sophisticated NLP parser for complex queries
- Interactive visualizations and Jupyter notebook support
- Ensemble simulation comparison
- Parameter sweep automation
- Web service wrapper

---

For questions or issues, see the main project [README.md](/README.md).

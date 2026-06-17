# Simulation Analysis Pipeline

A query-driven pipeline that wraps the deterministic predator–prey simulation in
[`DevelopmentSolution/`](../DevelopmentSolution/) to answer plain-language questions
about rabbit and fox populations, validate results against a hand-run baseline, and
generate **text** and **PDF** reports.

> **For AI assistants (Claude Code, Cursor, Gemini CLI, …)**: the pipeline is also
> exposed as an **MCP tool server** (`mcp_server.py`) for type-safe, structured tool
> access. See [MCP_INTEGRATION.md](MCP_INTEGRATION.md). For quick CLI access, see
> [.instructions.md](.instructions.md).

## Requirements

- **Python 3.10+** (tested on Python 3.12). The MCP SDK (`mcp`) requires ≥3.10; the
  simulation core (numpy 1.26 / matplotlib 3.8) requires ≥3.9.
- Git (to clone the repo).

## Setup

### One command

```bash
cd PipelineSolution
./setup.sh
```

`setup.sh` creates `.venv`, installs [`requirements.txt`](requirements.txt), verifies
imports (`test_imports.py`), and runs the unit tests (`tests/test_core.py`).

### Manual setup

```bash
cd PipelineSolution
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python test_imports.py
python -m unittest tests.test_core -q
```

### Verify installation

```bash
python test_imports.py
```

Expected (last lines):

```
✓ Ran micro simulation: returned arrays shape (6, 10, 10), (6, 10, 10)
  Final rabbit total: ..., final fox total: ...

✓ All imports and basic operations successful!
```

## Usage

### Plain-language queries (CLI)

```bash
# Ask for rabbit population at a specific timestep (text output)
python pipeline.py --query "How many rabbits at step 50?" --format text

# Ask for both species
python pipeline.py --query "What are the rabbit and fox populations at step 100?"

# Generate a full analysis report (PDF: summary page + time-series plot + final-step contour plots)
python pipeline.py --query "Generate a report for the default simulation" --format pdf --output report.pdf

# Override simulation parameters
python pipeline.py --query "Simulate with nx=40, ny=40 for 200 steps, then show foxes at step 150" --format text

# Validate against the hand-run baseline
python pipeline.py --query "Run the example configuration" --validate --format text
```

Or via the wrapper (auto-activates `.venv`):

```bash
./query.sh "How many foxes at step 180?"
./query.sh "Generate a PDF report" --format pdf --output report.pdf
./query.sh "50x50 grid, 360 steps, seed 12345" --validate
```

### MCP tools (for LLM clients)

`mcp_server.py` exposes five tools over the stdio MCP transport:
`query_population`, `run_simulation`, `generate_report`, `validate_baseline`,
`get_default_parameters`. See [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for client
configuration (Claude Code, Cursor, Gemini CLI) and examples.

## Architecture

```
Query Input (plain language)
    ↓
Parse & Validate          ← query_engine.py
    ↓
Build SimulationConfig    ← config_builder.py  (defaults from example_run/INPUTS.md)
    ↓
Execute Simulation        ← DevelopmentSolution/simulation.py  (via simulation_runner.py)
    ↓
Optionally Validate       ← validation.py  (vs DevelopmentSolution/example_run/ baseline)
    ↓
Generate Report           ← report_generator.py  (text or PDF)
    ↓
Output
```

### Key components

| File | Role |
|------|------|
| `pipeline.py` | CLI entry point and orchestrator |
| `query_engine.py` | Plain-language query parser (keyword/regex based) |
| `config_builder.py` | Converts parsed queries → `SimulationConfig` |
| `simulation_runner.py` | Runs simulations and exposes population accessors |
| `report_generator.py` | Text and PDF report generation |
| `validation.py` | Validates results against the `example_run` baseline |
| `mcp_server.py` | MCP tool server (FastMCP) for LLM clients |
| `test_imports.py` | Import smoke test |
| `tests/test_core.py` | Unit tests (parser, config builder, runner, validator) |
| `test_integration.sh` | End-to-end integration tests |
| `setup.sh` / `query.sh` | One-command setup / query wrapper |

## Configuration

Default parameters are inherited from [`DevelopmentSolution/example_run/INPUTS.md`](../DevelopmentSolution/example_run/INPUTS.md)
and encoded in `config_builder.py` (`DEFAULT_CONFIG`):

- Grid: 50×50 · Steps: 360 · `dt`: 0.06 · Seed: 12345
- Rabbit growth: 1.0 · Carrying capacity: 7.2 · Predation rate: 0.085
- Fox growth: 0.11 · Fox mortality: 0.72
- Diffusion: rabbit 0.01, fox 0.10
- Init: rabbit 2.4, fox 1.1, noise 0.07, patch strength 0.80, patch size 5

Override any parameter in a query with keywords like `nx=40`, `nt=200`, `seed=999`,
`50x50 grid`, `200 steps`, `fox_mortality=0.9`, etc.

## Validation against the hand-run baseline

The pipeline validates its output against the hand-run baseline in
`DevelopmentSolution/example_run/`:

- Parameters: as recorded in `INPUTS.md`
- Expected totals: from `population_counts.csv`

Run with `--validate` to check agreement within numerical tolerance (`1e-5`; the
underlying simulation is bit-identical to the baseline — the ~5e-7 residual is just the
6-decimal rounding in the stored CSV).

```bash
./query.sh "50x50 grid, 360 steps, seed 12345" --validate
# → Status: PASSED
```

## Tests

```bash
python -m unittest tests.test_core -v      # 17 unit tests
bash test_integration.sh                     # 6 end-to-end tests (incl. PDF + validation)
python test_imports.py                       # import smoke test
```

All pass on Python 3.12 with the pinned dependencies.

## Project structure

```
PipelineSolution/
├── README.md                 (this file)
├── requirements.txt           numpy, matplotlib, reportlab, mcp
├── setup.sh                   one-command setup
├── query.sh                   query wrapper (auto-activates venv)
├── pipeline.py                CLI entry point / orchestrator
├── query_engine.py            plain-language parser
├── config_builder.py          query → SimulationConfig
├── simulation_runner.py       simulation execution
├── report_generator.py        text + PDF reports
├── validation.py              baseline validation
├── mcp_server.py              MCP tool server (FastMCP)
├── claude_config.json          sample MCP client config (Claude Code)
├── test_imports.py            import smoke test
├── test_integration.sh        end-to-end integration tests
├── test_report.pdf            sample generated PDF report
├── tests/
│   ├── __init__.py
│   └── test_core.py           unit tests
├── .instructions.md           AI assistant instructions
├── AI_SETUP_GUIDE.md          AI-friendly setup guide
├── MCP_INTEGRATION.md         MCP server setup + tool reference
├── WHY_MCP.md                 rationale: query engine vs MCP
├── ARCHITECTURE_DECISION.md   architecture tradeoff notes
└── QUICKSTART.txt             one-page quick reference
```

## Reproducibility

All simulations use deterministic seeds (`np.random.default_rng(seed)`). To reproduce a
previous result, re-run with the same query/seed (the seed is reported in the output):

```bash
python pipeline.py --query "How many rabbits at step 50?" --seed 12345 --format text
```

PDF and text outputs include the configuration used, for full traceability.

## Known limitations

- The query parser is keyword/regex based; complex natural language is reduced to common
  request patterns. For free-form LLM input, prefer the MCP tools.
- PDF generation requires `reportlab`; text output does not.
- MCP support requires the `mcp` package (Python ≥3.10).
- Single-query model; no multi-turn dialogue or persistent state across runs.

## Future work

- Richer NLP parsing (or rely on LLM + MCP tools instead).
- Parameter sweeps and sensitivity analysis.
- Ensemble runs with uncertainty bands.
- Interactive/Jupyter visualizations.
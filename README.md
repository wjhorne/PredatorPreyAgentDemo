# PredatorPreyAgentDemo

This repository holds two reference solutions built with agentic AI:

- **[`DevelopmentSolution/`](DevelopmentSolution/)** — a deterministic 2D rabbit–fox predator–prey simulation (numpy + matplotlib) with a CLI for grid size, steps, and model parameters. This is the simulation engine the pipeline wraps.
- **[`PipelineSolution/`](PipelineSolution/)** — a query-driven analysis pipeline that wraps `DevelopmentSolution/`. It answers plain-language questions about rabbit/fox populations, validates results against a hand-run baseline, and produces both **text** and **PDF** reports. It also exposes an **MCP tool server** for LLM clients (Claude Code, Cursor, Gemini CLI).

## Quickstart

Requires **Python 3.10+** (tested on Python 3.12). `PipelineSolution` needs 3.10+ because it ships the MCP SDK; `DevelopmentSolution` alone needs 3.9+.

### Run the simulation — `DevelopmentSolution`

```bash
cd DevelopmentSolution
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --nx 50 --ny 50 --nt 360 --seed 12345 --no-show
```

This reproduces `DevelopmentSolution/example_run/population_counts.csv` exactly (the simulation is deterministic for a fixed seed). See [`DevelopmentSolution/README.md`](DevelopmentSolution/README.md).

### Run the analysis pipeline — `PipelineSolution`

```bash
cd PipelineSolution
./setup.sh                                            # one-command setup: venv, deps, tests
./query.sh "How many foxes at step 180?"               # plain-language query → text
./query.sh "Generate a PDF report" --format pdf --output report.pdf
./query.sh "50x50 grid, 360 steps, seed 12345" --validate   # exact-match vs hand-run baseline
```

For LLM/MCP usage (Claude Code, Cursor, Gemini CLI), see [`PipelineSolution/MCP_INTEGRATION.md`](PipelineSolution/MCP_INTEGRATION.md) and [`PipelineSolution/README.md`](PipelineSolution/README.md).

---

# Project specification

The sections below are the original project brief (read by anyone implementing a *new* solution). `DevelopmentSolution/` and `PipelineSolution/` are the provided reference baselines that new solutions are expected to differ from via a self-chosen novelty.

## Code Development Project Goal

Using agentic AI, build a small Python program that simulations rabbits and foxes on a 2D grid for Nt steps. Rabbits grow locally, foxes consume rabbits and grow based on their consumption, both diffuse to neighboring cells. Animate the result with matplotlib and report species populations at each time step. Provide a command line interface to specify grid size, steps, and key model parameters. Keep dependencies to numpy + matplotlib. 

## Code Development Instructions

With the agentic tool of your choice, start from an empty directory and use prompts to successfully create the requisite code. Test the resulting code by hand to roughly verify results. You may introduce the requirements below as a prompt, but the novelty must be one of your own choosing.

## Final Code Program Requirements

- The simulation must be based on feasible prey-predator dynamics whether equation based or otherwise
- Ensure that the language and dependencies requirements are held
- Results must be deterministic, use random seeds as necessary to achieve this
- The input of the program must be a grid_size (Nx, Ny), number of time steps Nt, and any relevant modeling parameters
- You must introduce one new novelty not found in the `DevelopmentSolution/` result for this task. For some potential examples:
    - Add a third species that is consumed by rabbits turning them into a predator
    - Use a particle-statistics simulation technique instead of diffusion + reaction equations to mimic the dynamics
    - Introduce distributed plant life that determines the growth of rabbits locally
    - Introduce terrain types within the grid that make things more difficult, or easier, for foxes or rabbits to enter

## Simulation Analysis Project Goal

Using agentic AI, create an agent based pipeline to run the predator-prey simulation code located in the `DevelopmentSolution/` folder. A user should be able to ask an agent in plain language to predict the number of rabbits or foxes at a specified time step and to produce corresponding plots of populations. Additionally the pipeline should be able to produce a `.pdf`report showing a contour plot of the populations at the final time step as well as a line plot of the populations over time.

## Simulation Analysis Instructions

Clone the PredatorPreyAgentDemo repo. With an agentic AI tool of your choice enter the repo directory and use prompts to create the pipeline. You may include the requirements below as part of your prompts, but the novelty must be of your own choice. Test the pipeline using the same agentic tool you used for creation of the pipeline. 

## Simulation Pipeline Requirements

- The pipeline must demonstrate that it exactly matches results from a hand-run result for at least one example set of inputs
- Plain language must be taken as input
- Both a `.pdf` report and text outputs must be supported
- Introduce one new novelty not found in `PipelineSolution`. For some examples:
  - Introduce the ability to perform parameter sweeps to assess survival scenarios for the rabbits or foxes
  - Create a goal-seeking capability where an agent could answer questions like `What rabbit reproduction rate keeps foxes alive past t = 200?`
  - Produce uncertainty bands of fox and rabbit populations via ensemble runs of different seeds
  - Introduce the ability to perform sensitivity analysis of results from the simulation to the parameters

# Development Plan: Predator-Prey Simulation (Python)

## 1. Objective
Build a deterministic, reproducible Python program in `DevelopmentSolution/` that simulates rabbit-fox dynamics on a 2D grid for `Nt` time steps, animates the grid state with matplotlib, and reports species populations at each step.

This plan is designed to satisfy the repository requirements:
- Feasible prey-predator dynamics
- Python with only `numpy` and `matplotlib`
- Deterministic results via fixed random seed handling
- CLI input for grid size, number of steps, and model parameters

## 2. Deliverables
Implement the following artifacts inside `DevelopmentSolution/`:

1. `main.py`
- CLI entry point
- Parses simulation parameters
- Runs simulation
- Prints rabbit/fox population totals per step
- Optionally saves/plays animation

2. `simulation.py`
- Core simulation model and update logic
- Deterministic random number generation via `numpy.random.Generator`
- Grid initialization and time stepping

3. `visualization.py`
- Matplotlib animation helpers
- Plot styling and frame update logic
- Optional output to GIF/MP4 if writer is available

4. `requirements.txt`
- Pinned runtime dependencies for reproducibility
- `numpy==<version>`
- `matplotlib==<version>`

5. `README.md` (inside `DevelopmentSolution/`)
- Setup instructions using Python virtual environments
- Exact run commands
- Parameter definitions
- Example deterministic run

6. `tests/` (lightweight, optional but recommended)
- Basic deterministic regression checks
- Parameter validation checks

## 3. Proposed Folder Structure

```text
DevelopmentSolution/
  PLAN.md
  README.md
  requirements.txt
  main.py
  simulation.py
  visualization.py
  tests/
    test_determinism.py
    test_shapes_and_nonnegative.py
```

## 4. Modeling Approach
Use a discrete-time, spatial predator-prey update on two `Nx x Ny` arrays:
- `R[t, i, j]`: rabbit density/count at cell `(i, j)`
- `F[t, i, j]`: fox density/count at cell `(i, j)`

At each step:
1. Rabbit local growth (logistic-like control)
2. Rabbit losses due to fox predation
3. Fox growth driven by predation intake
4. Fox natural mortality
5. Diffusion of both species to neighboring cells
6. Clamp to nonnegative values

A feasible deterministic update form:
- `R_next = R + a*R*(1 - R/K) - b*R*F + Dr*Laplacian(R)`
- `F_next = F + c*R*F - d*F + Df*Laplacian(F)`

Where:
- `a`: rabbit growth rate
- `K`: rabbit carrying capacity
- `b`: predation coefficient
- `c`: fox conversion efficiency
- `d`: fox mortality rate
- `Dr`, `Df`: diffusion rates

Use periodic boundary conditions for diffusion (`np.roll`) to keep implementation simple and stable.

## 5. Determinism Strategy

1. Use explicit CLI argument `--seed` with default fixed value (for example `12345`).
2. Use only one RNG source: `rng = np.random.default_rng(seed)`.
3. Use RNG only for initialization noise (if enabled), and document it clearly.
4. Ensure deterministic ordering of operations and avoid hidden randomness.
5. Add a quick regression test that runs the same input twice and asserts identical outputs.

## 6. CLI Requirements and Parameters
CLI must accept at least:
- `--nx` (int): grid width
- `--ny` (int): grid height
- `--nt` (int): number of time steps

Relevant model parameters (CLI flags):
- `--rabbit-growth` (`a`)
- `--carrying-capacity` (`K`)
- `--predation-rate` (`b`)
- `--fox-growth` (`c`)
- `--fox-mortality` (`d`)
- `--rabbit-diffusion` (`Dr`)
- `--fox-diffusion` (`Df`)
- `--dt` time step size
- `--seed` deterministic seed
- `--save-animation` output path (optional)
- `--no-show` disable interactive window for headless environments

Program output:
- Print one line per step with total rabbits and foxes, for example:
  - `step=0 rabbits=... foxes=...`

## 7. Reproducible Environment Plan

1. Require Python 3.11+ (or chosen target version) and document it.
2. Create isolated virtual environment:
   - `python3 -m venv .venv`
3. Activate environment:
   - Linux/macOS: `source .venv/bin/activate`
4. Install pinned dependencies:
   - `pip install -r requirements.txt`
5. Provide a minimal one-command run example in README.
6. Include a "clean rerun" section describing exact commands from clone to execution.

## 8. Implementation Steps

1. Scaffold files in `DevelopmentSolution/`.
2. Implement simulation core in `simulation.py`:
- Input validation (positive dimensions, nonnegative rates where appropriate)
- Initialization of rabbit/fox fields (seeded)
- Update equations and diffusion operator
- Time-series aggregation of total populations
3. Implement visualization in `visualization.py`:
- Side-by-side rabbit/fox heatmaps
- Frame title with current step and totals
- Animation object creation
4. Implement CLI in `main.py`:
- Parse arguments
- Run simulation
- Print totals each step
- Trigger animation display/save
5. Write `requirements.txt` with pinned versions.
6. Add `DevelopmentSolution/README.md` with setup and usage examples.
7. Add lightweight tests and run them.
8. Perform final deterministic verification run and record sample output in README.

## 9. Validation and Acceptance Criteria
The implementation is complete when all checks pass:

1. Requirements compliance
- Uses Python with `numpy` + `matplotlib` only
- Accepts `nx`, `ny`, `nt`, and relevant parameters via CLI
- Uses feasible predator-prey dynamics with diffusion
- Deterministic with seed

2. Functional checks
- Program runs from command line with provided arguments
- Species populations are printed every step
- Animation renders or saves correctly

3. Determinism checks
- Same parameters + same seed => identical outputs across runs
- Different seed can produce different initialization/outcomes (if stochastic init enabled)

4. Reproducibility checks
- Fresh clone + venv + `pip install -r requirements.txt` works
- Documented commands are sufficient for others to reproduce

## 10. Example Execution Commands (to include in README)

```bash
cd DevelopmentSolution
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --nx 80 --ny 80 --nt 200 --seed 12345 --no-show
```

Animation run example:

```bash
python main.py --nx 80 --ny 80 --nt 200 --seed 12345 --save-animation output.mp4
```

## 11. Risks and Mitigations

1. Numerical instability with large rates or `dt`
- Mitigation: conservative defaults, clamp nonnegative values, document stable ranges.

2. Headless environment issues for animation display
- Mitigation: provide `--no-show` and file save option.

3. Overly sparse/flat dynamics from poor defaults
- Mitigation: tune default parameters to show meaningful interaction.

## 12. Done Definition
Done means the code in `DevelopmentSolution/` can be built and run by another user from a clean clone using documented virtual environment steps, produces deterministic predator-prey simulation outputs, and satisfies every item in the Final Code Program Requirements.

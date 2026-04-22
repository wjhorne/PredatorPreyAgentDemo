# Development Solution: Predator-Prey Simulation

This folder contains a deterministic 2D rabbit-fox predator-prey simulation with diffusion.

## Requirements
- Python 3.8+
- Linux/macOS shell commands shown below (Windows PowerShell equivalents are straightforward)

## Reproducible Setup

```bash
cd DevelopmentSolution
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
python main.py --nx 80 --ny 80 --nt 200 --seed 12345
```

Headless run (no interactive window):

```bash
python main.py --nx 80 --ny 80 --nt 200 --seed 12345 --no-show
```

Save animation to file:

```bash
python main.py --nx 80 --ny 80 --nt 200 --seed 12345 --save-animation outputs/sim.gif --no-show
```

## CLI Parameters

Minimum required problem inputs are supported directly:
- `--nx`, `--ny`: grid dimensions
- `--nt`: number of time steps

Relevant model parameters:
- `--dt`
- `--rabbit-growth`
- `--carrying-capacity`
- `--predation-rate`
- `--fox-growth`
- `--fox-mortality`
- `--rabbit-diffusion`
- `--fox-diffusion`
- `--init-rabbit`
- `--init-fox`
- `--init-noise`
- `--init-patch-strength`
- `--init-patch-size`
- `--seed`

Initial-condition heterogeneity:
- `--init-patch-strength` controls the amplitude of coarse spatial patches.
- `--init-patch-size` controls the approximate patch width in grid cells.

Program output prints total populations each step:

```text
step=0 rabbits=... foxes=...
step=1 rabbits=... foxes=...
...
```

## Determinism
- The simulation is deterministic for fixed arguments and fixed `--seed`.
- Repeat runs with identical inputs produce identical population trajectories.

## Run Tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

#!/usr/bin/env python3
"""
Smoke test: verify DevelopmentSolution imports work from PipelineSolution.
Run this after installing requirements and setting PYTHONPATH.
"""
import sys
import os

# Add parent directory to path so DevelopmentSolution is importable
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

try:
    from DevelopmentSolution.simulation import (
        SimulationConfig,
        run_simulation,
    )
    print("✓ Imported SimulationConfig, run_simulation")
except ImportError as e:
    print(f"✗ Failed to import from DevelopmentSolution.simulation: {e}")
    sys.exit(1)

try:
    from DevelopmentSolution.visualization import (
        create_animation,
        render_animation,
    )
    print("✓ Imported create_animation, render_animation")
except ImportError as e:
    print(f"✗ Failed to import from DevelopmentSolution.visualization: {e}")
    sys.exit(1)

# Try instantiating a minimal config
try:
    config = SimulationConfig(
        nx=10, ny=10, nt=5, dt=0.06,
        rabbit_growth=1.0, carrying_capacity=7.2, predation_rate=0.085,
        fox_growth=0.11, fox_mortality=0.72,
        rabbit_diffusion=0.10, fox_diffusion=0.10,
        init_rabbit=2.4, init_fox=1.1, init_noise=0.07,
        init_patch_strength=0.0, init_patch_size=5,
        seed=12345,
    )
    print(f"✓ Created test SimulationConfig: {config.nx}x{config.ny}, {config.nt} steps, seed {config.seed}")
except Exception as e:
    print(f"✗ Failed to create SimulationConfig: {e}")
    sys.exit(1)

# Try running a micro simulation
try:
    result = run_simulation(config)
    rabbits = result["rabbits"]
    foxes = result["foxes"]
    rabbit_totals = result["rabbit_totals"]
    fox_totals = result["fox_totals"]
    print(f"✓ Ran micro simulation: returned arrays shape {rabbits.shape}, {foxes.shape}")
    print(f"  Final rabbit total: {rabbit_totals[-1]:.2f}, final fox total: {fox_totals[-1]:.2f}")
except Exception as e:
    print(f"✗ Failed to run simulation: {e}")
    sys.exit(1)

print("\n✓ All imports and basic operations successful!")

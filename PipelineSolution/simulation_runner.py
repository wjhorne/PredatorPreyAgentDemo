"""
Simulation runner: executes simulations with optional caching.

Provides utilities for accessing simulation results.
"""
import sys
import os
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from DevelopmentSolution.simulation import SimulationConfig, run_simulation


class SimulationRunner:
    """Execute simulations with optional result caching."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the runner.

        Args:
            cache_dir: Directory for caching results (default: ./.cache)
        """
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(__file__), ".cache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def run(self, config: SimulationConfig, use_cache: bool = True) -> Dict[str, Any]:
        """
        Run a simulation or retrieve cached result.

        Args:
            config: SimulationConfig to simulate
            use_cache: Whether to use cached results

        Returns:
            Dict with keys:
            - result: output from run_simulation() (dict with rabbits, foxes, totals)
            - config: the config used (for reference)
            - config_hash: hash of config for caching
            - cached: whether result was retrieved from cache
        """
        config_hash = self._hash_config(config)

        if use_cache:
            cached_result = self._load_cache(config_hash)
            if cached_result is not None:
                return {
                    "result": cached_result,
                    "config": config,
                    "config_hash": config_hash,
                    "cached": True,
                }

        # Run simulation
        result = run_simulation(config)

        # Cache result
        self._save_cache(config_hash, result)

        return {
            "result": result,
            "config": config,
            "config_hash": config_hash,
            "cached": False,
        }

    def _hash_config(self, config: SimulationConfig) -> str:
        """Generate a hash of the config for caching."""
        config_str = str(config)
        return hashlib.md5(config_str.encode()).hexdigest()

    def _load_cache(self, config_hash: str) -> Optional[Dict[str, Any]]:
        """Load cached result if it exists."""
        cache_file = self.cache_dir / f"{config_hash}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                # JSON doesn't support numpy arrays directly; load metadata only
                # The actual arrays would need custom serialization
                # For now, we skip array caching and just cache metadata
                return None  # Disable array caching for now
        except Exception:
            return None

    def _save_cache(self, config_hash: str, result: Dict[str, Any]) -> None:
        """Save result to cache (metadata only for now)."""
        # Array caching disabled; only metadata could be cached
        pass


def run_and_get_totals(config: SimulationConfig) -> Dict[str, Any]:
    """
    Convenience function: run simulation and return population totals.

    Args:
        config: SimulationConfig to simulate

    Returns:
        Dict with:
        - rabbit_totals: array of total rabbits per timestep
        - fox_totals: array of total foxes per timestep
        - rabbits: full spatial array (nt+1, nx, ny)
        - foxes: full spatial array (nt+1, nx, ny)
    """
    result = run_simulation(config)
    return {
        "rabbit_totals": result["rabbit_totals"],
        "fox_totals": result["fox_totals"],
        "rabbits": result["rabbits"],
        "foxes": result["foxes"],
    }


def get_population_at_step(
    rabbit_totals, fox_totals, timestep: int
) -> Dict[str, float]:
    """
    Get population values at a specific timestep.

    Args:
        rabbit_totals: Array of total rabbits per timestep
        fox_totals: Array of total foxes per timestep
        timestep: Index of timestep (0-based)

    Returns:
        Dict with rabbit and fox totals at that step
    """
    if timestep < 0 or timestep >= len(rabbit_totals):
        raise ValueError(f"Timestep {timestep} out of range [0, {len(rabbit_totals)-1}]")

    return {
        "rabbit": float(rabbit_totals[timestep]),
        "fox": float(fox_totals[timestep]),
    }

"""
Baseline validation: compare pipeline results against hand-run golden reference.

Loads the example_run baseline and provides validation functions.
"""
import sys
import os
import csv
from pathlib import Path
from typing import Dict, Any, Tuple

# Add parent directory to path for imports
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

import numpy as np
from DevelopmentSolution.simulation import SimulationConfig


class BaselineValidator:
    """Validate results against the example_run golden baseline."""

    def __init__(self):
        """Initialize the validator with the example_run baseline."""
        self.baseline_dir = Path(repo_root) / "DevelopmentSolution" / "example_run"
        self.baseline_params_file = self.baseline_dir / "INPUTS.md"
        self.baseline_csv_file = self.baseline_dir / "population_counts.csv"

        # Load baseline data
        self.baseline_totals = self._load_baseline_csv()
        self.baseline_params = self._load_baseline_params()

    def _load_baseline_csv(self) -> Dict[str, np.ndarray]:
        """Load population totals from population_counts.csv."""
        if not self.baseline_csv_file.exists():
            raise FileNotFoundError(f"Baseline CSV not found: {self.baseline_csv_file}")

        rabbit_totals = []
        fox_totals = []

        try:
            with open(self.baseline_csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Handle both "rabbit_total"/"rabbit_population" and "fox_total"/"fox_population"
                    rabbit_val = row.get("rabbit_total") or row.get("rabbit_population", 0)
                    fox_val = row.get("fox_total") or row.get("fox_population", 0)
                    rabbit_totals.append(float(rabbit_val))
                    fox_totals.append(float(fox_val))
        except Exception as e:
            raise ValueError(f"Failed to load baseline CSV: {e}")

        return {
            "rabbit_totals": np.array(rabbit_totals),
            "fox_totals": np.array(fox_totals),
        }

    def _load_baseline_params(self) -> Dict[str, Any]:
        """Parse baseline parameters from INPUTS.md."""
        if not self.baseline_params_file.exists():
            raise FileNotFoundError(f"Baseline params file not found: {self.baseline_params_file}")

        params = {}
        try:
            with open(self.baseline_params_file, "r") as f:
                in_params_section = False
                for line in f:
                    if "Parameters Used" in line:
                        in_params_section = True
                        continue

                    if in_params_section:
                        if line.strip().startswith("-") or line.strip().startswith("*"):
                            # Parse "- key: value" or "- key: value"
                            parts = line.strip().lstrip("-* ").split(":")
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value_str = parts[1].strip()

                                # Try to parse as int or float
                                try:
                                    if "." in value_str:
                                        params[key] = float(value_str)
                                    else:
                                        params[key] = int(value_str)
                                except ValueError:
                                    params[key] = value_str
                        elif line.strip() == "" or not line.startswith("-"):
                            # End of parameters section
                            if len(params) > 10:  # Sanity check
                                break
        except Exception as e:
            raise ValueError(f"Failed to parse baseline params: {e}")

        return params

    def validate_exact_match(
        self,
        rabbit_totals: np.ndarray,
        fox_totals: np.ndarray,
        tolerance: float = 1e-5,
    ) -> Tuple[bool, str]:
        """
        Validate exact match against baseline (with floating-point tolerance).

        Args:
            rabbit_totals: Array of total rabbits per timestep from pipeline
            fox_totals: Array of total foxes per timestep from pipeline
            tolerance: Max allowed difference per value

        Returns:
            Tuple of (passed: bool, message: str)
        """
        baseline_rabbit = self.baseline_totals["rabbit_totals"]
        baseline_fox = self.baseline_totals["fox_totals"]

        if len(rabbit_totals) != len(baseline_rabbit):
            return (
                False,
                f"Length mismatch: got {len(rabbit_totals)} steps, baseline has {len(baseline_rabbit)}",
            )

        if len(fox_totals) != len(baseline_fox):
            return (
                False,
                f"Length mismatch: got {len(fox_totals)} steps, baseline has {len(baseline_fox)}",
            )

        # Check rabbits
        rabbit_diff = np.abs(rabbit_totals - baseline_rabbit)
        rabbit_max_diff = np.max(rabbit_diff)
        if rabbit_max_diff > tolerance:
            return (
                False,
                f"Rabbit mismatch: max diff {rabbit_max_diff:.2e} exceeds tolerance {tolerance:.2e}",
            )

        # Check foxes
        fox_diff = np.abs(fox_totals - baseline_fox)
        fox_max_diff = np.max(fox_diff)
        if fox_max_diff > tolerance:
            return (
                False,
                f"Fox mismatch: max diff {fox_max_diff:.2e} exceeds tolerance {tolerance:.2e}",
            )

        return True, "✓ Validation PASSED: exact match within tolerance"

    def get_baseline_info(self) -> Dict[str, Any]:
        """Return information about the baseline."""
        baseline_rabbit = self.baseline_totals["rabbit_totals"]
        baseline_fox = self.baseline_totals["fox_totals"]

        return {
            "params": self.baseline_params,
            "num_steps": len(baseline_rabbit),
            "rabbit_stats": {
                "min": float(baseline_rabbit.min()),
                "max": float(baseline_rabbit.max()),
                "mean": float(baseline_rabbit.mean()),
                "final": float(baseline_rabbit[-1]),
            },
            "fox_stats": {
                "min": float(baseline_fox.min()),
                "max": float(baseline_fox.max()),
                "mean": float(baseline_fox.mean()),
                "final": float(baseline_fox[-1]),
            },
        }


def validate_baseline(
    rabbit_totals: np.ndarray,
    fox_totals: np.ndarray,
    tolerance: float = 1e-5,
) -> Tuple[bool, str]:
    """
    Convenience function: validate against baseline.

    Args:
        rabbit_totals: Array of total rabbits per timestep
        fox_totals: Array of total foxes per timestep
        tolerance: Max allowed difference per value

    Returns:
        Tuple of (passed: bool, message: str)
    """
    validator = BaselineValidator()
    return validator.validate_exact_match(rabbit_totals, fox_totals, tolerance)

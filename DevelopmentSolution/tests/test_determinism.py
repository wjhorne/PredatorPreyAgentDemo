import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation import SimulationConfig, run_simulation


class DeterminismTests(unittest.TestCase):
    def test_same_seed_produces_identical_results(self):
        config = SimulationConfig(nx=20, ny=15, nt=40, seed=2026)

        run_a = run_simulation(config)
        run_b = run_simulation(config)

        np.testing.assert_array_equal(run_a["rabbits"], run_b["rabbits"])
        np.testing.assert_array_equal(run_a["foxes"], run_b["foxes"])
        np.testing.assert_array_equal(run_a["rabbit_totals"], run_b["rabbit_totals"])
        np.testing.assert_array_equal(run_a["fox_totals"], run_b["fox_totals"])


if __name__ == "__main__":
    unittest.main()

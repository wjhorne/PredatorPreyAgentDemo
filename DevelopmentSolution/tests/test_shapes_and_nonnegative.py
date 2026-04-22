import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation import SimulationConfig, run_simulation


class ShapeAndDomainTests(unittest.TestCase):
    def test_output_shapes_and_nonnegative_populations(self):
        config = SimulationConfig(nx=12, ny=14, nt=10, seed=7)
        result = run_simulation(config)

        self.assertEqual(result["rabbits"].shape, (11, 12, 14))
        self.assertEqual(result["foxes"].shape, (11, 12, 14))
        self.assertEqual(result["rabbit_totals"].shape, (11,))
        self.assertEqual(result["fox_totals"].shape, (11,))

        self.assertTrue(np.all(result["rabbits"] >= 0.0))
        self.assertTrue(np.all(result["foxes"] >= 0.0))

    def test_invalid_configuration_raises(self):
        with self.assertRaises(ValueError):
            run_simulation(SimulationConfig(nx=0, ny=10, nt=5))


if __name__ == "__main__":
    unittest.main()

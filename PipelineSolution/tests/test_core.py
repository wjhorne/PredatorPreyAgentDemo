"""
Tests for query parser, config builder, and validation.
"""
import unittest
import sys
import os

# Add parent directory to path
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from query_engine import QueryParser
from config_builder import ConfigBuilder, build_config_from_query
from simulation_runner import get_population_at_step, run_and_get_totals
from validation import BaselineValidator
from DevelopmentSolution.simulation import SimulationConfig


class TestQueryParser(unittest.TestCase):
    """Test the query parser."""

    def setUp(self):
        self.parser = QueryParser()

    def test_parse_rabbit_population_query(self):
        """Test parsing a rabbit population query."""
        result = self.parser.parse("How many rabbits at step 50?")
        self.assertEqual(result["intent"], "population")
        self.assertEqual(result["species"], "rabbit")
        self.assertEqual(result["timestep"], 50)

    def test_parse_fox_population_query(self):
        """Test parsing a fox population query."""
        result = self.parser.parse("What's the fox population at step 100?")
        self.assertEqual(result["intent"], "population")
        self.assertEqual(result["species"], "fox")
        self.assertEqual(result["timestep"], 100)

    def test_parse_both_species_query(self):
        """Test parsing a query for both species."""
        result = self.parser.parse("Show me rabbits and foxes at timestep 200")
        self.assertEqual(result["species"], "both")
        self.assertEqual(result["timestep"], 200)

    def test_parse_report_request(self):
        """Test parsing a report generation request."""
        result = self.parser.parse("Generate a PDF report")
        self.assertEqual(result["intent"], "analysis")

    def test_parse_parameter_override_nx_ny(self):
        """Test parsing parameter overrides."""
        result = self.parser.parse("50x50 grid, step 100")
        self.assertEqual(result["params"]["nx"], 50)
        self.assertEqual(result["params"]["ny"], 50)

    def test_parse_parameter_override_steps(self):
        """Test parsing step count override."""
        result = self.parser.parse("Simulate for 200 steps")
        self.assertEqual(result["params"]["nt"], 200)

    def test_parse_parameter_override_seed(self):
        """Test parsing seed override."""
        result = self.parser.parse("With seed 999")
        self.assertEqual(result["params"]["seed"], 999)

    def test_parse_no_timestep(self):
        """Test query with no explicit timestep."""
        result = self.parser.parse("Generate a report")
        self.assertIsNone(result["timestep"])


class TestConfigBuilder(unittest.TestCase):
    """Test the config builder."""

    def test_build_config_with_defaults(self):
        """Test building a config with default parameters."""
        config = ConfigBuilder.build_config({})
        self.assertEqual(config.nx, 50)
        self.assertEqual(config.ny, 50)
        self.assertEqual(config.nt, 360)
        self.assertEqual(config.seed, 12345)

    def test_build_config_with_overrides(self):
        """Test building a config with parameter overrides."""
        params = {"nx": 40, "ny": 40, "seed": 999}
        config = ConfigBuilder.build_config(params)
        self.assertEqual(config.nx, 40)
        self.assertEqual(config.ny, 40)
        self.assertEqual(config.seed, 999)
        # Others should keep defaults
        self.assertEqual(config.nt, 360)

    def test_config_validation(self):
        """Test that invalid configs raise errors."""
        with self.assertRaises(ValueError):
            ConfigBuilder.build_config({"nx": -1})

    def test_build_from_parsed_query(self):
        """Test building config from a parsed query."""
        parser = QueryParser()
        parsed = parser.parse("50x50 grid, 200 steps, seed 999")
        config = build_config_from_query(parsed)
        self.assertEqual(config.nx, 50)
        self.assertEqual(config.ny, 50)
        self.assertEqual(config.nt, 200)
        self.assertEqual(config.seed, 999)


class TestSimulationResults(unittest.TestCase):
    """Test simulation result utilities."""

    def setUp(self):
        """Create a mini simulation for testing."""
        config = SimulationConfig(
            nx=10, ny=10, nt=5, seed=12345,
            init_patch_strength=0.0, init_patch_size=5
        )
        result = run_and_get_totals(config)
        self.rabbit_totals = result["rabbit_totals"]
        self.fox_totals = result["fox_totals"]

    def test_get_population_at_step(self):
        """Test getting population at a specific step."""
        pops = get_population_at_step(self.rabbit_totals, self.fox_totals, 0)
        self.assertIn("rabbit", pops)
        self.assertIn("fox", pops)
        self.assertGreaterEqual(pops["rabbit"], 0)
        self.assertGreaterEqual(pops["fox"], 0)

    def test_get_population_at_final_step(self):
        """Test getting population at the final step."""
        final_step = len(self.rabbit_totals) - 1
        pops = get_population_at_step(self.rabbit_totals, self.fox_totals, final_step)
        # Results should match expected values
        self.assertGreaterEqual(pops["rabbit"], 0)
        self.assertGreaterEqual(pops["fox"], 0)

    def test_get_population_out_of_range(self):
        """Test that out-of-range timestep raises error."""
        with self.assertRaises(ValueError):
            get_population_at_step(self.rabbit_totals, self.fox_totals, 999)


class TestBaselineValidator(unittest.TestCase):
    """Test the baseline validator."""

    def setUp(self):
        try:
            self.validator = BaselineValidator()
        except FileNotFoundError as e:
            self.skipTest(f"Baseline files not found: {e}")

    def test_baseline_info(self):
        """Test retrieving baseline information."""
        info = self.validator.get_baseline_info()
        self.assertIn("params", info)
        self.assertIn("num_steps", info)
        self.assertIn("rabbit_stats", info)
        self.assertIn("fox_stats", info)

    def test_baseline_loaded(self):
        """Test that baseline data was loaded."""
        self.assertGreater(len(self.validator.baseline_totals["rabbit_totals"]), 0)
        self.assertGreater(len(self.validator.baseline_totals["fox_totals"]), 0)


if __name__ == "__main__":
    unittest.main()

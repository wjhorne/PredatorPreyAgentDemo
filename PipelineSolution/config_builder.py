"""
Config builder: converts parsed queries to SimulationConfig objects.

Uses example_run parameters as defaults.
"""
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from DevelopmentSolution.simulation import SimulationConfig


# Default configuration from example_run/INPUTS.md
DEFAULT_CONFIG = {
    "nx": 50,
    "ny": 50,
    "nt": 360,
    "dt": 0.06,
    "seed": 12345,
    "rabbit_growth": 1.0,
    "carrying_capacity": 7.2,
    "predation_rate": 0.085,
    "fox_growth": 0.11,
    "fox_mortality": 0.72,
    "rabbit_diffusion": 0.01,
    "fox_diffusion": 0.10,
    "init_rabbit": 2.4,
    "init_fox": 1.1,
    "init_noise": 0.07,
    "init_patch_strength": 0.80,
    "init_patch_size": 5,
}


class ConfigBuilder:
    """Build SimulationConfig from parsed query parameters."""

    @staticmethod
    def build_config(params: Dict[str, Any]) -> SimulationConfig:
        """
        Build a SimulationConfig by merging user params with defaults.

        Args:
            params: Dict of parameter overrides from the parser

        Returns:
            SimulationConfig instance

        Raises:
            ValueError: If the resulting config is invalid
        """
        # Start with defaults
        config_dict = DEFAULT_CONFIG.copy()

        # Merge in user overrides
        config_dict.update(params)

        # Create and validate the config
        try:
            config = SimulationConfig(**config_dict)
            config.validate()
            return config
        except TypeError as e:
            raise ValueError(f"Invalid configuration: {e}")
        except ValueError as e:
            raise ValueError(f"Configuration validation failed: {e}")

    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """Return the default configuration parameters."""
        return DEFAULT_CONFIG.copy()


def build_config_from_query(parsed_query: Dict[str, Any]) -> SimulationConfig:
    """
    Convenience function: build config from parsed query dict.

    Args:
        parsed_query: Output from QueryParser.parse()

    Returns:
        SimulationConfig instance
    """
    return ConfigBuilder.build_config(parsed_query.get("params", {}))

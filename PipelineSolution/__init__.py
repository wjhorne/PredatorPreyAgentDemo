"""
Simulation Analysis Pipeline

A query-driven pipeline that wraps the deterministic predator-prey simulation
to answer plain-language queries about rabbit and fox populations, and to
generate analysis reports in text and PDF formats.

Modules:
  - query_engine: Plain-language query parsing
  - config_builder: Convert queries to SimulationConfig
  - simulation_runner: Execute simulations with caching
  - report_generator: Generate text and PDF reports
  - validation: Compare against hand-run baselines
  - pipeline: Main orchestrator and CLI entry point
"""

__version__ = "0.1.0"
__author__ = "Simulation Analysis Team"

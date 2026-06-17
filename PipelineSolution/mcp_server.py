"""
MCP (Model Context Protocol) Server for the Predator-Prey Simulation Pipeline.

Exposes the pipeline as tools that LLMs (Claude Code, Cursor, Gemini CLI, etc.)
can call directly with structured, type-safe parameters. This is the
recommended interface for LLM-based use; see ``MCP_INTEGRATION.md``.

The server uses the official MCP Python SDK's ``FastMCP`` high-level API and
speaks the stdio transport (the default for Claude Code / Cursor / Gemini CLI).

Run (from the PipelineSolution directory, with the venv activated):

    python mcp_server.py

Or register it in your client config (see ``claude_config.json`` /
``MCP_INTEGRATION.md``).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

# Make the repo root importable so `DevelopmentSolution` and the pipeline
# modules can be imported regardless of the client's working directory.
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from mcp.server.fastmcp import FastMCP

from DevelopmentSolution.simulation import SimulationConfig  # noqa: F401
from config_builder import ConfigBuilder, DEFAULT_CONFIG
from simulation_runner import get_population_at_step, run_and_get_totals
from report_generator import TextReportGenerator, PDFReportGenerator
from validation import BaselineValidator


mcp = FastMCP("predator-prey-simulation")


def _build_config(**overrides) -> SimulationConfig:
    """Build a validated SimulationConfig from keyword overrides merged onto defaults."""
    return ConfigBuilder.build_config(overrides)


@mcp.tool()
def query_population(
    species: str,
    timestep: int,
    nx: int = 50,
    ny: int = 50,
    nt: int = 360,
    seed: int = 12345,
) -> str:
    """Query the rabbit and/or fox population at a specific timestep.

    Args:
        species: Which species to report: "rabbit", "fox", or "both".
        timestep: Timestep index to query (0 through nt, inclusive).
        nx, ny: Grid dimensions (default 50x50, the example_run baseline).
        nt: Number of timesteps to simulate (default 360).
        seed: Deterministic RNG seed (default 12345).
    """
    config = _build_config(nx=nx, ny=ny, nt=nt, seed=seed)
    result = run_and_get_totals(config)
    pops = get_population_at_step(result["rabbit_totals"], result["fox_totals"], timestep)

    lines = [f"Population at timestep {timestep}:"]
    if species in ("rabbit", "both"):
        lines.append(f"- Rabbits: {pops['rabbit']:.2f}")
    if species in ("fox", "both"):
        lines.append(f"- Foxes: {pops['fox']:.2f}")
    return "\n".join(lines)


@mcp.tool()
def run_simulation(
    nx: int = 50,
    ny: int = 50,
    nt: int = 360,
    seed: int = 12345,
    rabbit_growth: float = 1.0,
    carrying_capacity: float = 7.2,
    predation_rate: float = 0.085,
    fox_growth: float = 0.11,
    fox_mortality: float = 0.72,
    rabbit_diffusion: float = 0.01,
    fox_diffusion: float = 0.10,
) -> str:
    """Run a simulation and return population statistics as JSON.

    All parameters are optional and default to the example_run baseline.
    """
    config = _build_config(
        nx=nx,
        ny=ny,
        nt=nt,
        seed=seed,
        rabbit_growth=rabbit_growth,
        carrying_capacity=carrying_capacity,
        predation_rate=predation_rate,
        fox_growth=fox_growth,
        fox_mortality=fox_mortality,
        rabbit_diffusion=rabbit_diffusion,
        fox_diffusion=fox_diffusion,
    )
    result = run_and_get_totals(config)
    rt, ft = result["rabbit_totals"], result["fox_totals"]
    stats = {
        "config": {
            "grid": f"{config.nx}x{config.ny}",
            "timesteps": config.nt,
            "seed": config.seed,
        },
        "rabbits": {
            "initial": float(rt[0]),
            "final": float(rt[-1]),
            "min": float(rt.min()),
            "max": float(rt.max()),
            "mean": float(rt.mean()),
        },
        "foxes": {
            "initial": float(ft[0]),
            "final": float(ft[-1]),
            "min": float(ft.min()),
            "max": float(ft.max()),
            "mean": float(ft.mean()),
        },
    }
    return f"Simulation complete:\n{json.dumps(stats, indent=2)}"


@mcp.tool()
def generate_report(
    format: str,
    output_file: str | None = None,
    nx: int = 50,
    ny: int = 50,
    nt: int = 360,
    seed: int = 12345,
) -> str:
    """Generate a text or PDF report for a simulation.

    Args:
        format: Output format, either "text" or "pdf".
        output_file: Path to save the report. If omitted, text is returned
            inline and a PDF is auto-named with a timestamp.
        nx, ny, nt, seed: Simulation parameters (default to example_run baseline).
    """
    config = _build_config(nx=nx, ny=ny, nt=nt, seed=seed)
    result = run_and_get_totals(config)

    if format == "text":
        report = TextReportGenerator.generate_text(
            config, result["rabbit_totals"], result["fox_totals"]
        )
        if output_file:
            with open(output_file, "w") as f:
                f.write(report)
            return f"Text report saved to {output_file}"
        return report

    if format == "pdf":
        path = output_file or f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        PDFReportGenerator.generate_pdf(
            config,
            result["rabbit_totals"],
            result["fox_totals"],
            result["rabbits"],
            result["foxes"],
            path,
        )
        return f"PDF report generated: {path}"

    return f"Error: unknown format '{format}' (use 'text' or 'pdf')"


@mcp.tool()
def validate_baseline(seed: int = 12345) -> str:
    """Validate the pipeline against the hand-run golden baseline (example_run).

    The baseline was generated with the example_run parameters (50x50 grid,
    360 steps). Passing a seed other than 12345 will not match the baseline.
    """
    config = _build_config(nx=50, ny=50, nt=360, seed=seed)
    result = run_and_get_totals(config)
    validator = BaselineValidator()
    passed, message = validator.validate_exact_match(
        result["rabbit_totals"], result["fox_totals"]
    )
    status = "PASSED" if passed else "FAILED"
    return f"{status}: {message}"


@mcp.tool()
def get_default_parameters() -> str:
    """Return the default simulation parameters (the example_run baseline)."""
    return f"Default parameters:\n{json.dumps(DEFAULT_CONFIG, indent=2)}"


def main() -> None:
    """Run the MCP server over stdio (the default transport for IDE clients)."""
    mcp.run()


if __name__ == "__main__":
    main()
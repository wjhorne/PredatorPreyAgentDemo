"""
MCP (Model Context Protocol) Server for Predator-Prey Simulation

Exposes simulation capabilities as tools that LLMs can call directly.
Much better than parsing natural language queries.

Run this server to enable Claude Code, Gemini, Copilot to call simulation tools.
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from DevelopmentSolution.simulation import SimulationConfig, run_simulation
from config_builder import ConfigBuilder, DEFAULT_CONFIG
from simulation_runner import get_population_at_step, run_and_get_totals
from report_generator import TextReportGenerator, PDFReportGenerator
from validation import BaselineValidator

try:
    from mcp.server import Server
    from mcp.types import TextContent, Tool
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp")
    sys.exit(1)


class SimulationMCPServer:
    """MCP Server that exposes simulation functions as tools."""

    def __init__(self):
        self.server = Server("predator-prey-simulation")
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""
        
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="query_population",
                    description="Query population at a specific timestep",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "species": {
                                "type": "string",
                                "enum": ["rabbit", "fox", "both"],
                                "description": "Which species to query",
                            },
                            "timestep": {
                                "type": "integer",
                                "description": "Timestep to query (0-360)",
                            },
                            "nx": {
                                "type": "integer",
                                "description": "Grid width (default: 50)",
                            },
                            "ny": {
                                "type": "integer",
                                "description": "Grid height (default: 50)",
                            },
                            "nt": {
                                "type": "integer",
                                "description": "Number of timesteps (default: 360)",
                            },
                            "seed": {
                                "type": "integer",
                                "description": "Random seed (default: 12345)",
                            },
                        },
                        "required": ["species", "timestep"],
                    },
                ),
                Tool(
                    name="run_simulation",
                    description="Run a simulation and get population statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "nx": {
                                "type": "integer",
                                "description": "Grid width (default: 50)",
                            },
                            "ny": {
                                "type": "integer",
                                "description": "Grid height (default: 50)",
                            },
                            "nt": {
                                "type": "integer",
                                "description": "Number of timesteps (default: 360)",
                            },
                            "seed": {
                                "type": "integer",
                                "description": "Random seed (default: 12345)",
                            },
                            "rabbit_growth": {
                                "type": "number",
                                "description": "Rabbit growth rate (default: 1.0)",
                            },
                            "carrying_capacity": {
                                "type": "number",
                                "description": "Rabbit carrying capacity (default: 7.2)",
                            },
                            "predation_rate": {
                                "type": "number",
                                "description": "Predation rate (default: 0.085)",
                            },
                            "fox_growth": {
                                "type": "number",
                                "description": "Fox growth rate (default: 0.11)",
                            },
                            "fox_mortality": {
                                "type": "number",
                                "description": "Fox mortality rate (default: 0.72)",
                            },
                            "rabbit_diffusion": {
                                "type": "number",
                                "description": "Rabbit diffusion (default: 0.01)",
                            },
                            "fox_diffusion": {
                                "type": "number",
                                "description": "Fox diffusion (default: 0.10)",
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="generate_report",
                    description="Generate a text or PDF report of the simulation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "format": {
                                "type": "string",
                                "enum": ["text", "pdf"],
                                "description": "Output format",
                            },
                            "output_file": {
                                "type": "string",
                                "description": "Path to save report (optional)",
                            },
                            "nx": {
                                "type": "integer",
                                "description": "Grid width (default: 50)",
                            },
                            "ny": {
                                "type": "integer",
                                "description": "Grid height (default: 50)",
                            },
                            "nt": {
                                "type": "integer",
                                "description": "Number of timesteps (default: 360)",
                            },
                            "seed": {
                                "type": "integer",
                                "description": "Random seed (default: 12345)",
                            },
                        },
                        "required": ["format"],
                    },
                ),
                Tool(
                    name="validate_baseline",
                    description="Validate simulation against the hand-run golden baseline",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "seed": {
                                "type": "integer",
                                "description": "Random seed (default: 12345)",
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="get_default_parameters",
                    description="Get the default simulation parameters",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            try:
                if name == "query_population":
                    return await self._query_population(arguments)
                elif name == "run_simulation":
                    return await self._run_simulation(arguments)
                elif name == "generate_report":
                    return await self._generate_report(arguments)
                elif name == "validate_baseline":
                    return await self._validate_baseline(arguments)
                elif name == "get_default_parameters":
                    return await self._get_default_parameters(arguments)
                else:
                    return TextContent(type="text", text=f"Unknown tool: {name}")
            except Exception as e:
                return TextContent(type="text", text=f"Error: {str(e)}")

    async def _query_population(self, args: dict):
        """Query population at a specific timestep."""
        species = args.get("species", "both")
        timestep = args.get("timestep")

        if timestep is None:
            return TextContent(
                type="text",
                text="Error: timestep is required",
            )

        # Build config with optional overrides
        config_params = {}
        for key in ["nx", "ny", "nt", "seed"]:
            if key in args:
                config_params[key] = args[key]

        config = ConfigBuilder.build_config(config_params)

        # Run simulation
        result = run_and_get_totals(config)
        pops = get_population_at_step(
            result["rabbit_totals"],
            result["fox_totals"],
            timestep,
        )

        # Format response
        response = f"**Population at timestep {timestep}:**\n"
        if species in ("rabbit", "both"):
            response += f"- Rabbits: {pops['rabbit']:.2f}\n"
        if species in ("fox", "both"):
            response += f"- Foxes: {pops['fox']:.2f}\n"

        return TextContent(type="text", text=response)

    async def _run_simulation(self, args: dict):
        """Run simulation and return statistics."""
        # Build config with provided parameters
        config = ConfigBuilder.build_config(args)

        # Run simulation
        result = run_and_get_totals(config)
        rabbit_totals = result["rabbit_totals"]
        fox_totals = result["fox_totals"]

        # Gather statistics
        stats = {
            "config": {
                "grid": f"{config.nx}×{config.ny}",
                "timesteps": config.nt,
                "seed": config.seed,
            },
            "rabbits": {
                "initial": float(rabbit_totals[0]),
                "final": float(rabbit_totals[-1]),
                "min": float(rabbit_totals.min()),
                "max": float(rabbit_totals.max()),
                "mean": float(rabbit_totals.mean()),
            },
            "foxes": {
                "initial": float(fox_totals[0]),
                "final": float(fox_totals[-1]),
                "min": float(fox_totals.min()),
                "max": float(fox_totals.max()),
                "mean": float(fox_totals.mean()),
            },
        }

        return TextContent(
            type="text",
            text=f"Simulation complete:\n{json.dumps(stats, indent=2)}",
        )

    async def _generate_report(self, args: dict):
        """Generate a text or PDF report."""
        format_type = args.get("format", "text")
        output_file = args.get("output_file")

        # Build config
        config_params = {}
        for key in ["nx", "ny", "nt", "seed"]:
            if key in args:
                config_params[key] = args[key]
        config = ConfigBuilder.build_config(config_params)

        # Run simulation
        result = run_and_get_totals(config)

        if format_type == "text":
            report = TextReportGenerator.generate_text(
                config,
                result["rabbit_totals"],
                result["fox_totals"],
            )

            if output_file:
                with open(output_file, "w") as f:
                    f.write(report)
                return TextContent(
                    type="text",
                    text=f"✓ Text report saved to {output_file}",
                )
            else:
                return TextContent(type="text", text=report)

        elif format_type == "pdf":
            if not output_file:
                output_file = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            PDFReportGenerator.generate_pdf(
                config,
                result["rabbit_totals"],
                result["fox_totals"],
                result["rabbits"],
                result["foxes"],
                output_file,
            )
            return TextContent(
                type="text",
                text=f"✓ PDF report generated: {output_file}",
            )

        else:
            return TextContent(
                type="text",
                text=f"Error: unknown format {format_type}",
            )

    async def _validate_baseline(self, args: dict):
        """Validate against the golden baseline."""
        seed = args.get("seed", 12345)

        config_params = {
            "nx": 50,
            "ny": 50,
            "nt": 360,
            "seed": seed,
        }
        config = ConfigBuilder.build_config(config_params)

        result = run_and_get_totals(config)
        validator = BaselineValidator()
        passed, message = validator.validate_exact_match(
            result["rabbit_totals"],
            result["fox_totals"],
        )

        status = "✓ PASSED" if passed else "✗ FAILED"
        return TextContent(
            type="text",
            text=f"{status}: {message}",
        )

    async def _get_default_parameters(self, args: dict):
        """Return default configuration parameters."""
        defaults = ConfigBuilder.get_defaults()
        return TextContent(
            type="text",
            text=f"Default parameters:\n{json.dumps(defaults, indent=2)}",
        )

    async def run(self):
        """Run the MCP server."""
        async with self.server:
            print("✓ Predator-Prey Simulation MCP Server running")
            print("Available tools:")
            print("  - query_population: Get population at timestep")
            print("  - run_simulation: Run simulation with parameters")
            print("  - generate_report: Generate text or PDF report")
            print("  - validate_baseline: Check against golden baseline")
            print("  - get_default_parameters: Show defaults")
            await self.server.wait()


def main():
    """Main entry point."""
    import asyncio

    server = SimulationMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()

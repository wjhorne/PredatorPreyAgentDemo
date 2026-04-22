#!/usr/bin/env python3
"""
Simulation Analysis Pipeline: main entry point.

Orchestrates: query parsing → config building → simulation → validation → reporting.
"""
import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path so DevelopmentSolution is importable
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

from DevelopmentSolution.simulation import SimulationConfig, run_simulation

from query_engine import QueryParser
from config_builder import build_config_from_query
from simulation_runner import get_population_at_step, run_and_get_totals
from report_generator import TextReportGenerator, PDFReportGenerator
from validation import validate_baseline


def build_parser():
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Query the predator-prey simulation pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --query "How many rabbits at step 50?"
  python pipeline.py --query "Show me foxes and rabbits" --format pdf
  python pipeline.py --query "Simulate with nx=40, ny=40" --format text
  python pipeline.py --query "50x50 grid, 200 steps" --validate
        """,
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Plain-language query or parameter specification",
    )
    parser.add_argument(
        "--format",
        choices=["text", "pdf"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: stdout for text, auto-named for PDF)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate against example_run baseline after simulation",
    )
    return parser


def main():
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        # Parse query
        print(f"[Pipeline] Parsing query: {args.query[:60]}...")
        query_parser = QueryParser()
        parsed_query = query_parser.parse(args.query)

        intent = parsed_query["intent"]
        species = parsed_query["species"]
        timestep = parsed_query["timestep"]

        # Build config
        print("[Pipeline] Building configuration...")
        config = build_config_from_query(parsed_query)

        # Run simulation
        print("[Pipeline] Running simulation...")
        result = run_and_get_totals(config)
        rabbit_totals = result["rabbit_totals"]
        fox_totals = result["fox_totals"]
        rabbits_spatial = result["rabbits"]
        foxes_spatial = result["foxes"]

        # Optionally validate against baseline
        validation_result = None
        if args.validate:
            print("[Pipeline] Validating against baseline...")
            passed, message = validate_baseline(rabbit_totals, fox_totals)
            validation_result = (passed, message)
            if passed:
                print(f"  {message}")
            else:
                print(f"  ✗ {message}")

        # Generate output
        print(f"[Pipeline] Generating {args.format} output...")

        if args.format == "text":
            # Text output
            text_report = TextReportGenerator.generate_text(
                config=config,
                rabbit_totals=rabbit_totals,
                fox_totals=fox_totals,
                species=species,
                timestep=timestep,
                validation_result=validation_result,
            )

            if args.output:
                with open(args.output, "w") as f:
                    f.write(text_report)
                print(f"✓ Text report saved to: {args.output}")
            else:
                print(text_report)

        elif args.format == "pdf":
            # PDF output
            if not args.output:
                # Auto-generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                args.output = f"simulation_report_{timestamp}.pdf"

            PDFReportGenerator.generate_pdf(
                config=config,
                rabbit_totals=rabbit_totals,
                fox_totals=fox_totals,
                rabbits_spatial=rabbits_spatial,
                foxes_spatial=foxes_spatial,
                output_path=args.output,
            )
            print(f"✓ PDF report saved to: {args.output}")

        print("[Pipeline] ✓ Completed successfully!")
        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

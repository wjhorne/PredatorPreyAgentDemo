"""
Report generator: creates text and PDF outputs for simulation results.
"""
import sys
import os
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from reportlab.pdfgen import canvas

from DevelopmentSolution.simulation import SimulationConfig


class TextReportGenerator:
    """Generate plain-text reports."""

    @staticmethod
    def generate_text(
        config: SimulationConfig,
        rabbit_totals: np.ndarray,
        fox_totals: np.ndarray,
        species: str = "both",
        timestep: Optional[int] = None,
        validation_result: Optional[tuple] = None,
    ) -> str:
        """
        Generate a text report.

        Args:
            config: SimulationConfig used
            rabbit_totals: Array of rabbit totals per timestep
            fox_totals: Array of fox totals per timestep
            species: "rabbit", "fox", or "both"
            timestep: Specific timestep to report (or None for summary)
            validation_result: Tuple of (passed: bool, message: str) or None

        Returns:
            Formatted text report
        """
        lines = []

        # Header
        lines.append("=" * 70)
        lines.append("SIMULATION ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")

        # Configuration
        lines.append("CONFIGURATION")
        lines.append("-" * 70)
        lines.append(f"Grid size:              {config.nx} × {config.ny}")
        lines.append(f"Time steps:             {config.nt}")
        lines.append(f"Seed:                   {config.seed}")
        lines.append(f"Rabbit growth rate:     {config.rabbit_growth}")
        lines.append(f"Carrying capacity:      {config.carrying_capacity}")
        lines.append(f"Predation rate:         {config.predation_rate}")
        lines.append(f"Fox growth rate:        {config.fox_growth}")
        lines.append(f"Fox mortality rate:     {config.fox_mortality}")
        lines.append(f"Rabbit diffusion:       {config.rabbit_diffusion}")
        lines.append(f"Fox diffusion:          {config.fox_diffusion}")
        lines.append("")

        # Population statistics
        lines.append("POPULATION STATISTICS")
        lines.append("-" * 70)
        lines.append(f"Species: {species.upper()}")
        lines.append("")

        if species in ("rabbit", "both"):
            lines.append("RABBITS:")
            lines.append(f"  Initial population:    {rabbit_totals[0]:>12.2f}")
            lines.append(f"  Final population:      {rabbit_totals[-1]:>12.2f}")
            lines.append(f"  Minimum:               {rabbit_totals.min():>12.2f}")
            lines.append(f"  Maximum:               {rabbit_totals.max():>12.2f}")
            lines.append(f"  Mean:                  {rabbit_totals.mean():>12.2f}")
            lines.append(f"  Std Dev:               {rabbit_totals.std():>12.2f}")

            if timestep is not None:
                if 0 <= timestep < len(rabbit_totals):
                    lines.append(f"  Population at step {timestep}: {rabbit_totals[timestep]:>10.2f}")
            lines.append("")

        if species in ("fox", "both"):
            lines.append("FOXES:")
            lines.append(f"  Initial population:    {fox_totals[0]:>12.2f}")
            lines.append(f"  Final population:      {fox_totals[-1]:>12.2f}")
            lines.append(f"  Minimum:               {fox_totals.min():>12.2f}")
            lines.append(f"  Maximum:               {fox_totals.max():>12.2f}")
            lines.append(f"  Mean:                  {fox_totals.mean():>12.2f}")
            lines.append(f"  Std Dev:               {fox_totals.std():>12.2f}")

            if timestep is not None:
                if 0 <= timestep < len(fox_totals):
                    lines.append(f"  Population at step {timestep}: {fox_totals[timestep]:>10.2f}")
            lines.append("")

        # Validation result
        if validation_result is not None:
            lines.append("VALIDATION")
            lines.append("-" * 70)
            passed, message = validation_result
            lines.append(f"Status: {'PASSED' if passed else 'FAILED'}")
            lines.append(f"Message: {message}")
            lines.append("")

        # Footer
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)

        return "\n".join(lines)


class PDFReportGenerator:
    """Generate PDF reports with plots."""

    @staticmethod
    def generate_pdf(
        config: SimulationConfig,
        rabbit_totals: np.ndarray,
        fox_totals: np.ndarray,
        rabbits_spatial: np.ndarray,
        foxes_spatial: np.ndarray,
        output_path: str,
    ) -> None:
        """
        Generate a multi-page PDF report with plots.

        Args:
            config: SimulationConfig used
            rabbit_totals: Array of rabbit totals per timestep
            fox_totals: Array of fox totals per timestep
            rabbits_spatial: Full spatial rabbit array (nt+1, nx, ny)
            foxes_spatial: Full spatial fox array (nt+1, nx, ny)
            output_path: Path to save PDF
        """
        with PdfPages(output_path) as pdf:
            # Page 1: Summary
            PDFReportGenerator._page_summary(
                pdf, config, rabbit_totals, fox_totals
            )

            # Page 2: Time series plot
            PDFReportGenerator._page_timeseries(
                pdf, rabbit_totals, fox_totals
            )

            # Page 3: Final spatial distributions (contour plots)
            PDFReportGenerator._page_contours(
                pdf, rabbits_spatial, foxes_spatial
            )

        print(f"✓ PDF report generated: {output_path}")

    @staticmethod
    def _page_summary(pdf, config, rabbit_totals, fox_totals):
        """Generate the summary page."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")

        # Title
        title_text = "Predator-Prey Simulation Report"
        ax.text(0.5, 0.95, title_text, ha="center", fontsize=16, weight="bold",
                transform=ax.transAxes)

        # Configuration table
        config_data = [
            ["Grid Size", f"{config.nx} × {config.ny}"],
            ["Time Steps", str(config.nt)],
            ["Seed", str(config.seed)],
            ["Rabbit Growth", f"{config.rabbit_growth:.4f}"],
            ["Carrying Capacity", f"{config.carrying_capacity:.4f}"],
            ["Predation Rate", f"{config.predation_rate:.4f}"],
            ["Fox Growth", f"{config.fox_growth:.4f}"],
            ["Fox Mortality", f"{config.fox_mortality:.4f}"],
            ["Rabbit Diffusion", f"{config.rabbit_diffusion:.4f}"],
            ["Fox Diffusion", f"{config.fox_diffusion:.4f}"],
        ]

        y_pos = 0.85
        for row in config_data:
            y_pos -= 0.04
            ax.text(0.1, y_pos, row[0], fontsize=10, weight="bold",
                    transform=ax.transAxes)
            ax.text(0.5, y_pos, row[1], fontsize=10, family="monospace",
                    transform=ax.transAxes)

        # Statistics
        y_pos -= 0.08
        ax.text(0.1, y_pos, "POPULATION STATISTICS", fontsize=12, weight="bold",
                transform=ax.transAxes)

        stats_data = [
            [f"Rabbits (initial)", f"{rabbit_totals[0]:.2f}"],
            [f"Rabbits (final)", f"{rabbit_totals[-1]:.2f}"],
            [f"Rabbits (mean)", f"{rabbit_totals.mean():.2f}"],
            [f"Foxes (initial)", f"{fox_totals[0]:.2f}"],
            [f"Foxes (final)", f"{fox_totals[-1]:.2f}"],
            [f"Foxes (mean)", f"{fox_totals.mean():.2f}"],
        ]

        y_pos -= 0.04
        for row in stats_data:
            y_pos -= 0.03
            ax.text(0.1, y_pos, row[0], fontsize=9, transform=ax.transAxes)
            ax.text(0.6, y_pos, row[1], fontsize=9, family="monospace",
                    transform=ax.transAxes)

        # Footer
        ax.text(0.5, 0.02, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ha="center", fontsize=9, style="italic", transform=ax.transAxes)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def _page_timeseries(pdf, rabbit_totals, fox_totals):
        """Generate the time-series plot page."""
        fig, ax = plt.subplots(figsize=(8.5, 6))

        timesteps = np.arange(len(rabbit_totals))

        ax.plot(timesteps, rabbit_totals, label="Rabbits", color="brown", linewidth=2)
        ax.plot(timesteps, fox_totals, label="Foxes", color="red", linewidth=2)

        ax.set_xlabel("Time Step", fontsize=11)
        ax.set_ylabel("Population", fontsize=11)
        ax.set_title("Population Over Time", fontsize=12, weight="bold")
        ax.legend(loc="best", fontsize=10)
        ax.grid(True, alpha=0.3)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def _page_contours(pdf, rabbits_spatial, foxes_spatial):
        """Generate the final spatial distribution contour plots."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

        # Rabbits at final timestep
        rabbit_final = rabbits_spatial[-1]
        im1 = ax1.contourf(rabbit_final, levels=20, cmap="YlOrRd")
        ax1.set_title("Rabbits (Final)", fontsize=11, weight="bold")
        ax1.set_xlabel("X")
        ax1.set_ylabel("Y")
        cbar1 = plt.colorbar(im1, ax=ax1)
        cbar1.set_label("Population per cell", fontsize=9)

        # Foxes at final timestep
        fox_final = foxes_spatial[-1]
        im2 = ax2.contourf(fox_final, levels=20, cmap="Reds")
        ax2.set_title("Foxes (Final)", fontsize=11, weight="bold")
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        cbar2 = plt.colorbar(im2, ax=ax2)
        cbar2.set_label("Population per cell", fontsize=9)

        fig.suptitle("Final Spatial Distributions", fontsize=12, weight="bold", y=1.00)

        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

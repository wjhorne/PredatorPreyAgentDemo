"""Visualization helpers for predator-prey simulation output."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, PowerNorm
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import StrMethodFormatter
import numpy as np


def _build_norm(vmin: float, vmax: float, gamma: float):
    if abs(gamma - 1.0) < 1e-12:
        return Normalize(vmin=vmin, vmax=vmax)
    return PowerNorm(gamma=gamma, vmin=vmin, vmax=vmax)


def _apply_colorbar(colorbar, vmin: float, vmax: float) -> None:
    ticks = np.linspace(vmin, vmax, 5)
    colorbar.set_ticks(ticks)
    colorbar.ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.2f}"))
    colorbar.update_ticks()


def create_animation(
    rabbits: np.ndarray,
    foxes: np.ndarray,
    interval_ms: int = 80,
    frame_stride: int = 1,
    rabbit_color_percentile: float = 99.0,
    fox_color_percentile: float = 99.0,
    rabbit_gamma: float = 1.0,
    fox_gamma: float = 1.0,
) -> FuncAnimation:
    if rabbits.shape != foxes.shape:
        raise ValueError("rabbits and foxes histories must have the same shape.")
    if frame_stride <= 0:
        raise ValueError("frame_stride must be a positive integer.")
    if rabbit_color_percentile <= 0.0 or rabbit_color_percentile > 100.0:
        raise ValueError("rabbit_color_percentile must be in the range (0, 100].")
    if fox_color_percentile <= 0.0 or fox_color_percentile > 100.0:
        raise ValueError("fox_color_percentile must be in the range (0, 100].")
    if rabbit_gamma <= 0.0:
        raise ValueError("rabbit_gamma must be > 0.")
    if fox_gamma <= 0.0:
        raise ValueError("fox_gamma must be > 0.")

    rabbit_totals = rabbits.sum(axis=(1, 2))
    fox_totals = foxes.sum(axis=(1, 2))
    frame_indices = np.arange(0, rabbits.shape[0], frame_stride)

    rabbit_vmin = float(np.min(rabbits))
    rabbit_vmax = float(np.percentile(rabbits, rabbit_color_percentile))
    fox_vmin = float(np.min(foxes))
    fox_vmax = float(np.percentile(foxes, fox_color_percentile))
    if rabbit_vmin == rabbit_vmax:
        rabbit_vmax = rabbit_vmin + 1e-12
    if fox_vmin == fox_vmax:
        fox_vmax = fox_vmin + 1e-12

    rabbit_norm = _build_norm(rabbit_vmin, rabbit_vmax, rabbit_gamma)
    fox_norm = _build_norm(fox_vmin, fox_vmax, fox_gamma)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), constrained_layout=True)

    rabbit_im = axes[0].imshow(rabbits[frame_indices[0]], cmap="YlGn", norm=rabbit_norm)
    fox_im = axes[1].imshow(foxes[frame_indices[0]], cmap="OrRd", norm=fox_norm)

    axes[0].set_title("Rabbits Per Cell")
    axes[1].set_title("Foxes Per Cell")
    axes[0].set_xlabel("y")
    axes[1].set_xlabel("y")
    axes[0].set_ylabel("x")

    rabbit_colorbar = fig.colorbar(rabbit_im, ax=axes[0], fraction=0.046)
    fox_colorbar = fig.colorbar(fox_im, ax=axes[1], fraction=0.046)
    _apply_colorbar(rabbit_colorbar, rabbit_vmin, rabbit_vmax)
    _apply_colorbar(fox_colorbar, fox_vmin, fox_vmax)
    rabbit_colorbar.set_label("rabbits per cell")
    fox_colorbar.set_label("foxes per cell")

    title = fig.suptitle("")

    def update(frame: int):
        step = int(frame_indices[frame])
        rabbit_im.set_data(rabbits[step])
        fox_im.set_data(foxes[step])
        title.set_text(
            f"step={step} total rabbits={rabbit_totals[step]:.3f} total foxes={fox_totals[step]:.3f}"
        )
        return rabbit_im, fox_im, title

    return FuncAnimation(
        fig,
        update,
        frames=frame_indices.size,
        interval=interval_ms,
        blit=False,
        repeat=False,
    )


def render_animation(anim: FuncAnimation, save_path: str | None, show: bool) -> None:
    if save_path:
        target = Path(save_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        anim.save(str(target), dpi=120)

    if show:
        plt.show()
    else:
        plt.close(anim._fig)

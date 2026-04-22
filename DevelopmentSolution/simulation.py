"""Core deterministic predator-prey simulation on a 2D grid."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SimulationConfig:
    nx: int = 80
    ny: int = 80
    nt: int = 200
    dt: float = 0.1
    seed: int = 12345

    rabbit_growth: float = 1.2
    carrying_capacity: float = 8.0
    predation_rate: float = 0.08
    fox_growth: float = 0.06
    fox_mortality: float = 0.9
    rabbit_diffusion: float = 0.18
    fox_diffusion: float = 0.12

    init_rabbit: float = 2.5
    init_fox: float = 1.0
    init_noise: float = 0.12
    init_patch_strength: float = 0.35
    init_patch_size: int = 6

    def validate(self) -> None:
        if self.nx <= 0 or self.ny <= 0:
            raise ValueError("Grid dimensions nx and ny must be positive integers.")
        if self.nt < 0:
            raise ValueError("nt must be >= 0.")
        if self.dt <= 0:
            raise ValueError("dt must be > 0.")

        nonnegative_params = {
            "rabbit_growth": self.rabbit_growth,
            "carrying_capacity": self.carrying_capacity,
            "predation_rate": self.predation_rate,
            "fox_growth": self.fox_growth,
            "fox_mortality": self.fox_mortality,
            "rabbit_diffusion": self.rabbit_diffusion,
            "fox_diffusion": self.fox_diffusion,
            "init_rabbit": self.init_rabbit,
            "init_fox": self.init_fox,
            "init_noise": self.init_noise,
            "init_patch_strength": self.init_patch_strength,
        }
        for name, value in nonnegative_params.items():
            if value < 0:
                raise ValueError(f"{name} must be >= 0.")

        if self.carrying_capacity <= 0:
            raise ValueError("carrying_capacity must be > 0.")
        if self.init_patch_size <= 0:
            raise ValueError("init_patch_size must be > 0.")


def _laplacian_periodic(field: np.ndarray) -> np.ndarray:
    return (
        np.roll(field, shift=1, axis=0)
        + np.roll(field, shift=-1, axis=0)
        + np.roll(field, shift=1, axis=1)
        + np.roll(field, shift=-1, axis=1)
        - 4.0 * field
    )


def _make_patch_field(
    rng: np.random.Generator,
    nx: int,
    ny: int,
    patch_size: int,
) -> np.ndarray:
    coarse_nx = int(np.ceil(nx / patch_size))
    coarse_ny = int(np.ceil(ny / patch_size))
    coarse = rng.normal(0.0, 1.0, size=(coarse_nx, coarse_ny))
    field = np.kron(coarse, np.ones((patch_size, patch_size), dtype=np.float64))[:nx, :ny]
    field -= field.mean()

    std = float(field.std())
    if std > 0.0:
        field /= std
    return field


def initialize_fields(config: SimulationConfig) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(config.seed)

    rabbit_patch = _make_patch_field(rng, config.nx, config.ny, config.init_patch_size)
    fox_patch = _make_patch_field(rng, config.nx, config.ny, config.init_patch_size)
    rabbit_noise = rng.normal(0.0, config.init_noise, size=(config.nx, config.ny))
    fox_noise = rng.normal(0.0, config.init_noise, size=(config.nx, config.ny))

    rabbits = np.clip(
        config.init_rabbit + config.init_patch_strength * rabbit_patch + rabbit_noise,
        0.0,
        None,
    )
    foxes = np.clip(
        config.init_fox + config.init_patch_strength * fox_patch + fox_noise,
        0.0,
        None,
    )
    return rabbits.astype(np.float64), foxes.astype(np.float64)


def _step(rabbits: np.ndarray, foxes: np.ndarray, config: SimulationConfig) -> tuple[np.ndarray, np.ndarray]:
    rabbit_growth_term = config.rabbit_growth * rabbits * (1.0 - rabbits / config.carrying_capacity)
    predation_term = config.predation_rate * rabbits * foxes
    fox_growth_term = config.fox_growth * rabbits * foxes
    fox_death_term = config.fox_mortality * foxes

    rabbits_next = rabbits + config.dt * (
        rabbit_growth_term
        - predation_term
        + config.rabbit_diffusion * _laplacian_periodic(rabbits)
    )
    foxes_next = foxes + config.dt * (
        fox_growth_term
        - fox_death_term
        + config.fox_diffusion * _laplacian_periodic(foxes)
    )

    return np.clip(rabbits_next, 0.0, None), np.clip(foxes_next, 0.0, None)


def run_simulation(config: SimulationConfig) -> dict[str, np.ndarray]:
    config.validate()

    rabbits_hist = np.zeros((config.nt + 1, config.nx, config.ny), dtype=np.float64)
    foxes_hist = np.zeros((config.nt + 1, config.nx, config.ny), dtype=np.float64)

    rabbits_hist[0], foxes_hist[0] = initialize_fields(config)

    for step in range(1, config.nt + 1):
        rabbits_hist[step], foxes_hist[step] = _step(rabbits_hist[step - 1], foxes_hist[step - 1], config)

    rabbit_totals = rabbits_hist.sum(axis=(1, 2))
    fox_totals = foxes_hist.sum(axis=(1, 2))

    return {
        "rabbits": rabbits_hist,
        "foxes": foxes_hist,
        "rabbit_totals": rabbit_totals,
        "fox_totals": fox_totals,
    }

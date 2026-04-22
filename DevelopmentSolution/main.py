"""CLI entry point for deterministic 2D predator-prey simulation."""

from __future__ import annotations

import argparse
import sys

from simulation import SimulationConfig, run_simulation
from visualization import create_animation, render_animation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="2D rabbit-fox predator-prey simulation")

    parser.add_argument("--nx", type=int, default=80, help="Grid x-size")
    parser.add_argument("--ny", type=int, default=80, help="Grid y-size")
    parser.add_argument("--nt", type=int, default=200, help="Number of time steps")
    parser.add_argument("--dt", type=float, default=0.1, help="Time step size")

    parser.add_argument("--rabbit-growth", type=float, default=1.2, help="Rabbit growth rate")
    parser.add_argument("--carrying-capacity", type=float, default=8.0, help="Rabbit carrying capacity")
    parser.add_argument("--predation-rate", type=float, default=0.08, help="Predation rate")
    parser.add_argument("--fox-growth", type=float, default=0.06, help="Fox growth from predation")
    parser.add_argument("--fox-mortality", type=float, default=0.9, help="Fox natural mortality")
    parser.add_argument("--rabbit-diffusion", type=float, default=0.18, help="Rabbit diffusion rate")
    parser.add_argument("--fox-diffusion", type=float, default=0.12, help="Fox diffusion rate")

    parser.add_argument("--init-rabbit", type=float, default=2.5, help="Initial rabbit baseline")
    parser.add_argument("--init-fox", type=float, default=1.0, help="Initial fox baseline")
    parser.add_argument("--init-noise", type=float, default=0.12, help="Stddev of initialization noise")
    parser.add_argument(
        "--init-patch-strength",
        type=float,
        default=0.35,
        help="Amplitude of coarse spatial patches in the initial condition",
    )
    parser.add_argument(
        "--init-patch-size",
        type=int,
        default=6,
        help="Approximate linear patch size in grid cells for initial-condition heterogeneity",
    )

    parser.add_argument("--seed", type=int, default=12345, help="Deterministic RNG seed")
    parser.add_argument("--save-animation", type=str, default=None, help="Optional file path to save animation")
    parser.add_argument(
        "--frame-stride",
        type=int,
        default=1,
        help="Use every Nth time step when rendering animation frames",
    )
    parser.add_argument(
        "--rabbit-color-percentile",
        type=float,
        default=99.0,
        help="Use this run-wide percentile as fixed vmax for the rabbit color axis",
    )
    parser.add_argument(
        "--fox-color-percentile",
        type=float,
        default=99.0,
        help="Use this run-wide percentile as fixed vmax for the fox color axis",
    )
    parser.add_argument(
        "--rabbit-gamma",
        type=float,
        default=1.0,
        help="Power-law gamma for rabbit color scaling; values > 1 reduce high-end blowout",
    )
    parser.add_argument(
        "--fox-gamma",
        type=float,
        default=1.0,
        help="Power-law gamma for fox color scaling",
    )
    parser.add_argument("--no-show", action="store_true", help="Do not open a matplotlib window")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    config = SimulationConfig(
        nx=args.nx,
        ny=args.ny,
        nt=args.nt,
        dt=args.dt,
        seed=args.seed,
        rabbit_growth=args.rabbit_growth,
        carrying_capacity=args.carrying_capacity,
        predation_rate=args.predation_rate,
        fox_growth=args.fox_growth,
        fox_mortality=args.fox_mortality,
        rabbit_diffusion=args.rabbit_diffusion,
        fox_diffusion=args.fox_diffusion,
        init_rabbit=args.init_rabbit,
        init_fox=args.init_fox,
        init_noise=args.init_noise,
        init_patch_strength=args.init_patch_strength,
        init_patch_size=args.init_patch_size,
    )

    try:
        results = run_simulation(config)
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    rabbit_totals = results["rabbit_totals"]
    fox_totals = results["fox_totals"]

    for step, (rabbit_total, fox_total) in enumerate(zip(rabbit_totals, fox_totals)):
        print(f"step={step} rabbits={rabbit_total:.6f} foxes={fox_total:.6f}")

    show = not args.no_show
    if show or args.save_animation:
        anim = create_animation(
            results["rabbits"],
            results["foxes"],
            frame_stride=args.frame_stride,
            rabbit_color_percentile=args.rabbit_color_percentile,
            fox_color_percentile=args.fox_color_percentile,
            rabbit_gamma=args.rabbit_gamma,
            fox_gamma=args.fox_gamma,
        )
        render_animation(anim, save_path=args.save_animation, show=show)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

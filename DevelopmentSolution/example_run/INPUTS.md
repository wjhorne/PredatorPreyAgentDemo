# Example Run Inputs

This run uses a stronger patchy initial condition to increase spatial heterogeneity while keeping the deterministic dynamics stable.

## Parameters Used
- nx: 50
- ny: 50
- nt: 360
- dt: 0.06
- seed: 12345
- rabbit_growth: 1.0
- carrying_capacity: 7.2
- predation_rate: 0.085
- fox_growth: 0.11
- fox_mortality: 0.72
- rabbit_diffusion: 0.01
- fox_diffusion: 0.10
- init_rabbit: 2.4
- init_fox: 1.1
- init_noise: 0.07
- init_patch_strength: 0.80
- init_patch_size: 5

## Animation Settings
- frame_stride: 9
- rabbit_color_percentile: 100
- fox_color_percentile: 99
- rabbit_gamma: 1.0
- fox_gamma: 1.0

## Reproducible Run Command

Run this from `DevelopmentSolution/` with the virtual environment activated:

```bash
python main.py \
	--nx 50 \
	--ny 50 \
	--nt 360 \
	--dt 0.06 \
	--seed 12345 \
	--rabbit-growth 1.0 \
	--carrying-capacity 7.2 \
	--predation-rate 0.085 \
	--fox-growth 0.11 \
	--fox-mortality 0.72 \
	--rabbit-diffusion 0.01 \
	--fox-diffusion 0.10 \
	--init-rabbit 2.4 \
	--init-fox 1.1 \
	--init-noise 0.07 \
	--init-patch-strength 0.80 \
	--init-patch-size 5 \
	--frame-stride 9 \
	--rabbit-color-percentile 100 \
	--fox-color-percentile 99 \
	--rabbit-gamma 1.0 \
	--fox-gamma 1.0 \
	--save-animation example_run/simulation.gif \
	--no-show
```

## Survival and Steady-State Indicator (Final 50 Steps)
- mean absolute rabbit change per step: 1.417105
- mean absolute fox change per step: 2.271934
- relative rabbit drift: 0.000084
- relative fox drift: 0.001158
- final rabbit population: 16823.405316
- final fox population: 1962.345985

## Output Notes
- population_counts.csv includes all steps from 0 through nt.
- simulation.gif uses every 9th step for faster rendering.
- Rabbit colors use the full run-wide maximum with linear scaling and formatted ticks for a cleaner colorbar.
- Fox colors use a 99th-percentile fixed vmax with gamma 1.0.
- Heatmap colorbars show per-cell population values; the title and CSV report totals summed over the entire grid.

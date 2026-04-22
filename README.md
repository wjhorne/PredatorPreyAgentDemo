## Code Development Project Goal

Using agentic AI, build a small Python program that simulations rabbits and foxes on a 2D grid for Nt steps. Rabbits grow locally, foxes consume rabbits and grow based on their consumption, both diffuse to neighboring cells. Animate the result with matplotlib and report species populations at each time step. Provide a command line interface to specify grid size, steps, and key model parameters. Keep dependencies to numpy + matplotlib. 

## Final Code Program Requirements

- The simulation must be based on feasible prey-predator dynamics whether equation based or otherwise
- Ensure that the language and dependencies requirements are held
- Results must be deterministic, use random seeds as necessary to achieve this
- The input of the program must be a grid_size (Nx, Ny), number of time steps Nt, and any relevant modeling parameters

## Simulation Analysis Project Goal

Using agentic AI, create an agent based pipeline to run the predator-prey simulation code located in the `DevelopmentSolution/` folder. A user should be able to ask an agent in plain language to predict the number of rabbits or foxes at a specified time step and to produce corresponding plots of populations. Additionally the pipeline should be able to produce a `.pdf`report showing a contour plot of the populations at the final time step as well as a line plot of the populations over time.

## Simulation Pipeline Requirements

- The pipeline must demonstrate that it exactly matches results from a hand-run result for at least one example set of inputs
- Plain language must be taken as input
- Both a `.pdf` report and text outputs must be supported
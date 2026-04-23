## Code Development Project Goal

Using agentic AI, build a small Python program that simulations rabbits and foxes on a 2D grid for Nt steps. Rabbits grow locally, foxes consume rabbits and grow based on their consumption, both diffuse to neighboring cells. Animate the result with matplotlib and report species populations at each time step. Provide a command line interface to specify grid size, steps, and key model parameters. Keep dependencies to numpy + matplotlib. 

## Code Development Instructions

With the agentic tool of your choice, start from an empty directory and use prompts to successfully create the requisite code. Test the resulting code by hand to roughly verify results. You may introduce the requirements below as a prompt, but the novelty must be one of your own choosing.

**Example using Gemini**
- install gemini-cli as appropriate for your workstation
- mkdir project_directory
- cd project_directory
- gemini -s
- Use oauth to log into your Gemini account
- prompt the agent as necessary

## Final Code Program Requirements

- The simulation must be based on feasible prey-predator dynamics whether equation based or otherwise
- Ensure that the language and dependencies requirements are held
- Results must be deterministic, use random seeds as necessary to achieve this
- The input of the program must be a grid_size (Nx, Ny), number of time steps Nt, and any relevant modeling parameters
- You must introduce one new novelty not found in the `DevelopmentSolution/` result for this task. For some potential examples:
    - Add a third species that is consumed by rabbits turning them into a predator
    - Use a particle-statistics simulation technique instead of diffusion + reaction equations to mimic the dynamics
    - Introduce distributed plant life that determines the growth of rabbits locally
    - Introduce terrain types within the grid that make things more difficult, or easier, for foxes or rabbits to enter

## Simulation Analysis Project Goal

Using agentic AI, create an agent based pipeline to run the predator-prey simulation code located in the `DevelopmentSolution/` folder. A user should be able to ask an agent in plain language to predict the number of rabbits or foxes at a specified time step and to produce corresponding plots of populations. Additionally the pipeline should be able to produce a `.pdf`report showing a contour plot of the populations at the final time step as well as a line plot of the populations over time.

## Simulation Analysis Instructions

Clone the PredatorPreyAgentDemo repo. With an agentic AI tool of your choice enter the repo directory and use prompts to create the pipeline. Test the pipeline using the same agentic tool you used for creation of the pipeline. 

**Example using Gemini**

- install gemini-cli as appropriate for your workstation
- git clone git@github.com:wjhorne/PredatorPreyAgentDemo.git
- cd PredatorPreyAgentDemo
- gemini -s
- Use oauth to log into your Gemini account
- prompt the agent as necessary to create the pipeline inside of a folder within PredatorPreyAgentDemo

**To test the pipeline**
- cd PredatorPreyAgentDemo
- gemini -s
- Use oauth to log into your Gemini acount
- prompt the agent to parse your project directory for the pipeline
- Ask the agent pipeline test questions to show requirements are fulfilled 

## Simulation Pipeline Requirements

- The pipeline must demonstrate that it exactly matches results from a hand-run result for at least one example set of inputs
- Plain language must be taken as input
- Both a `.pdf` report and text outputs must be supported
- Introduce one new novelty not found in `PipelineSolution`. For some examples:
  - Introduce the ability to perform parameter sweeps to assess survival scenarios for the rabbits or foxes
  - Create a goal-seeking capability where an agent could answer questions like `What rabbit reproduction rate keeps foxes alive past t = 200?`
  - Produce uncertainty bands of fox and rabbit populations via ensemble runs of different seeds
  - Introduce the ability to perform sensitivity analysis of results from the simulation to the parameters

# Reinforcement Learning for Factor Rotation

## Run the server

```bash
bash run_server.sh
```

## Classes

### Env

The environment class is the main class for the environment. It contains the step function, the reset function and hosts
the agent.

### Agent

The agent class contains the code for the agent.

### Data

The data class contains the code for the data.

### Experiment

The experiment class contains the code for the experiment.

## Things we need to decide on:

- Do we want to compare against a benchmark
- What observation space we want to use
- How do we backtest/step to next outcome

## Data:

- Few simple factor etfs as the investment space
- Store a simple data frame as data feed

## Tasks:

Tasks and open todos can be seen in the [Projects section](https://github.zhaw.ch/davidjaggi/rl-factor-rotation/projects/1).

- [ ] Implement Environment reset() function that randomizes starting dates of the portfolios and resets the broker (and thus the datafeed) accordingly. 
- [ ] Implement Environment step() function that translates actions (discrete for now) into ideal_weights changes and calls the rebalancing schedule /rebalance functions, and finally calculates rewards. 
- [ ] Implement Environment tests for random actions + visualization functionalities to graph portfolios (benchmark vs RL) across Episodes.


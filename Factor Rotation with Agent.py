# %%
# TODO implement a custom experiment class
# https://github.com/ray-project/ray/issues/9220#issue-648483764
# %%
import matplotlib.pyplot as plt
import numpy as np
from ray.rllib.agents.ppo import PPOTrainer
from ray.tune.registry import register_env

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.create_env import create_env
from src.experiment.custom_experiment import CustomExperiment
from src.utils.load_path import load_data_path

# %%
data_path = load_data_path()
feed = CSVDataFeed(file_name=data_path + "/example_data.csv")

ENV_CONFIG = {
    "initial_balance": 10000,
    "initial_weights": np.array([0.5, 0.5]),
    "benchmark_type": "custom",
    "benchmark_wgts": np.array([0.5, 0.5]),
    "start_date": "2015-12-31",
    "end_date": "2020-12-31",
    "busday_offset_start": 250,
    "cost_pct": 0.0005,
    "reward_scaling": 1,
    "obs_price_hist": 5,
}

# now try a different rebalancing frequency...
schedule = PeriodicSchedule(frequency="WOM-3FRI")

env_config = {
    "data_feed": feed,
    "config": ENV_CONFIG,
    "rebalance_schedule": schedule,
}

# %%
# register the environment
register_env("base_env", create_env)

config = {
    "env": "base_env",
    "env_config": env_config,
    "num_workers": 2,
    "num_gpus": 0}

# %%
experiment = CustomExperiment(
    config=config,
    env="base_env",
    agent=PPOTrainer,
    save_dir="./results")

# %%
# first we train the agent
experiment.train(stop_criteria={"timesteps_total": 10000})
# %%
# load the trained agent
experiment.load(
    path="./results/PPOTrainer_2022-09-08_16-49-39/PPOTrainer_base_env_770b7_00000_0_2022-09-08_16-49-39/checkpoint_000003/checkpoint-3")
# %%
reward = experiment.test()
# %%
# plot the rewards of the agent
plt.plot(reward)
plt.title("Rewards")
plt.show()

# %%
# TODO implement a custom experiment class
# https://github.com/ray-project/ray/issues/9220#issue-648483764
# %%
from datetime import date

import matplotlib.pyplot as plt
import ray
from ray.rllib.agents.ppo import PPOTrainer
from ray.tune.registry import register_env

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.create_env import create_env
from src.env.portfolio import BenchmarkPortfolio, RLPortfolio
from src.experiment.custom_experiment import CustomExperiment
from src.utils.load_path import load_data_path

# %%
ray.shutdown()
data_path = load_data_path()
feed = CSVDataFeed(file_name=data_path + "/example_factor_clean.csv")
ENV_CONFIG = {
    'benchmark_portfolio': {
        'name': 'benchmark_portfolio',
        'rebalancing_type': "equally_weighted",
        'investment_universe': ["MKT_Index", "SMB_Index", 'HML_Index', 'RF_Index'],
        'initial_balance': int(10000),
        'initial_weights': [0.25, 0.25, 0.25, 0.25],
        'restrictions': dict(),
        'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
    },
    'rl_portfolio': {
        'name': 'rl_portfolio',
        'rebalancing_type': None,
        'investment_universe': ["MKT_Index", "SMB_Index", 'HML_Index', 'RF_Index'],
        'initial_balance': int(10000),
        'initial_weights': [0.25, 0.25, 0.25, 0.25],
        'restrictions': dict(),
        'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
    },
    'broker': {
        "rl_portfolio": None,
        "benchmark_portfolio": None,
        "start_date": date(2010, 12, 31),
        "end_date": date(2020, 12, 31),
        "busday_offset_start": 250,
        "transaction_cost": 0.05
    },
    'agent': {
        "reward_scaling": int(1),
        "obs_price_hist": int(250),
    }
}

ENV_CONFIG['broker']['rl_portfolio'] = RLPortfolio(ENV_CONFIG['rl_portfolio'])
ENV_CONFIG['broker']['benchmark_portfolio'] = BenchmarkPortfolio(ENV_CONFIG['benchmark_portfolio'])

# now try a different rebalancing frequency...
schedule = PeriodicSchedule(frequency="WOM-3FRI")

# %%
config = {
    "env": "base_env",
    "env_config": {
        "data_feed": feed,
        "config": ENV_CONFIG,
    },
    "num_workers": 1,
    "num_gpus": 0,
    "log_level": "INFO",
}

register_env("base_env", create_env)
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

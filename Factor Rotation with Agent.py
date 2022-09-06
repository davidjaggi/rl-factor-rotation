# %%
import matplotlib.pyplot as plt
import numpy as np
import ray
from ray.rllib.agents.ppo import PPOTrainer
from ray.tune.registry import register_env

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.utils.create_env import create_env
from src.utils.load_path import load_data_path

# %%
ray.init()

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


# %%
def test_agent(config=None):
    agent = PPOTrainer(config)
    env = create_env(config["env_config"])
    episode_reward = np.array([0])
    done = False
    obs = env.reset()
    while not done:
        action = agent.compute_single_action(obs)
        obs, rew, done, _ = env.step(action)
        episode_reward = np.append(episode_reward, rew)
    return episode_reward


# %%
config = {
    "env": "base_env",
    "env_config": env_config,
    "num_workers": 2,
    "num_gpus": 0}
reward = test_agent(config)
# %%
# plot the rewards of the agent
plt.plot(reward)
plt.title("Rewards")
plt.show()

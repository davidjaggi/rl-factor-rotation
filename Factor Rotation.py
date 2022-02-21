# %%
import numpy as np
from src.data.rebalancing_schedule import PeriodicSchedule
from src.data.feed import CSVDataFeed
from src.env.base_env import BaseEnv
import matplotlib.pyplot as plt

# %%
feed = CSVDataFeed(file_name="/workspaces/rl-factor-rotation/src/env/example_data.csv")

env_config = {
    "initial_balance": 10000,
    "benchmark_type": "custom",
    "benchmark_wgts": np.array([0.5, 0.5]),
    "start_date": "2018-12-31",
    "end_date": "2020-12-31",
    "busday_offset_start": 250,
    "cost_pct": 0.0005,
    "reward_scaling": 1,
    "obs_price_hist": 5,
}

# now try a different rebalancing frequency...
schedule = PeriodicSchedule(frequency="WOM-3FRI")
# %%
env = BaseEnv(data_feed=feed, config=env_config, rebalance_schedule=schedule)
obs = env.reset()
done = False
while not done:
    action = env.action_space.sample()
    # action = np.array([-1, 1])
    obs, rew, done, _ = env.step(action)
env.plot_current_performance()
plt.show()

# %%

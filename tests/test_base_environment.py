# %%
import random
import os
import gym

import numpy as np

from src.environment.base_environment import BaseEnvironment
from src.data.data_feed import BaseDataFeed

# %%
data_feed = BaseDataFeed(["AAPL", "MSFT"], "2020-01-01", "2020-12-31")

# check data
data_feed.data.head()

# check number of tickers
data_feed.num_tickers

# %%
# define the config
env_config = {}
# define action space
action_space = gym.spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
# define the env
base_env = BaseEnvironment(data_feed, config=env_config, action_space=action_space)

# %%
for i in range(50):
    seed = random.randint(0, 100000)

    # seed = 64360
    print(seed)
    random.seed(a=seed)

    # define the datafeed
    data_feed = BaseDataFeed(["AAPL", "MSFT","AAPL"], "2020-01-01", "2020-12-31")

    # define the config
    env_config = {}
    # define action space
    action_space = gym.spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
    # define the env
    base_env = BaseEnvironment(data_feed, config=env_config, action_space=action_space)

    for k in range(100):
        base_env.step(actions=np.array([0.05]))
        if base_env.terminal:
            print(base_env.reward)
            base_env.reset()
# %%

# %%

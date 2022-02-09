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
    data_feed = BaseDataFeed(["AAPL", "MSFT"], "2020-01-01", "2020-12-31")

    # define the config
    env_config = {}
    # define action space
    action_space = gym.spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
    # define the env
    base_env = BaseEnvironment(data_feed, config=env_config, action_space=action_space)

    # for i in range(10):
    #     t = time.time()
    #     broker.simulate_algo(broker.benchmark_algo)
    #     broker.benchmark_algo.plot_schedule(broker.trade_logs['benchmark_algo'])
    #     elapsed = time.time() - t
    #     print(elapsed)
    """
    for k in range(len(base_env.broker.rl_algo.algo_events) + 1):
        base_env.step(action=np.array([0.05]))
        if base_env.done:
            print(base_env.broker.benchmark_algo.bmk_vwap, base_env.broker.rl_algo.rl_vwap)
            print(base_env.reward)
            base_env.reset()
    """
# %%

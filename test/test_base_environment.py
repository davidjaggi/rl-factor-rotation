# %%
import unittest
import random
import gym

import numpy as np

from src.environment.base_environment import BaseEnvironment
from src.data.data_feed import BaseDataFeed


class TestBaseEnvironment(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.data_feed = BaseDataFeed(["AAPL", "MSFT"], "2020-01-01", "2020-12-31")
        self.config = {}
        self.action_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(1,), dtype=np.float32
        )

    def test_initialize(self):
        env = BaseEnvironment(
            self.data_feed, config=self.config, action_space=self.action_space
        )

        # self.assertFalse(env.initial, "Initial state is not False") need more information
        self.assertFalse(env.terminal, "Terminal state is not False")
        self.assertEqual(env.initial_balance, 10000, "Initial balance is not 10000")
        self.assertEqual(env.day, 0, "Day is not 0")
        self.assertEqual(env.reward, 0, "Reward is not 0")
        self.assertEqual(env.cost, 0, "Cost is not 0")
        self.assertEqual(env.trades, 0, "Trades is not 0")
        self.assertEqual(env.episode, 0, "Episode is not 0")
        print(env.data)

    def test_unique_tickers(self):
        env = BaseEnvironment(
            self.data_feed, config=self.config, action_space=self.action_space
        )
        self.assertEqual(
            len(env.df.ticker.unique()),
            2,
            "Number of unique tickers is not 2",
        )


"""
# %%
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
"""

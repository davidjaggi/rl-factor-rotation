# %%
import numpy as np
import gym
from gym.utils import seeding
import pandas as pd
import matplotlib.pyplot as plt
import itertools


# https://towardsdatascience.com/finrl-for-quantitative-finance-tutorial-for-multiple-stock-trading-7b00763b7530
# %%
BASE_CONFIG = {
    "portfolio_config": {"initial_balance": 10000},
    "benchmark_config": {"type": "equally_weighted"},
}

# %%
class BaseEnvironment(gym.Env):
    def __init__(self, data_feed, config, action_space):
        """Initialises the class"""

        self.data_feed = data_feed
        self.data = self.data_feed.data
        self.config = BASE_CONFIG | config
        print(self.config)
        self.action_space = action_space

        self.initial_balance = self.config["portfolio_config"]["initial_balance"]
        # initialize reward
        self.reward = 0
        self.initial = True
        self.trades = 0

        # initialize state
        self.state = self._initiate_state()

        self.reset()
        self._seed()

    def reset(self):
        # initialize state
        self.state = self._initiate_state()

        self.init_balance = self.config["portfolio_config"]["initial_balance"]
        self.reward = 0
        self.done = False
        self.state = self.build_observation()

    def step(self, action):
        assert self.done is False, "reset() must be called before step()"

        action = self._convert_action(action)

        self.time += 1

        self.reward = 0
        self.info = {}

        return self.state, self.reward, self.done, self.info

    def _convert_action(self, action):
        """Used if actions need to be transformed without having to change entire step() method"""
        return action

    def _initiate_state(self):
        if self.initial:
            # For Initial State
            if len(self.data_feed.data.ticker.unique()) > 1:
                # for multiple stock
                state = (
                    [self.initial_balance]
                    + self.data.close.values.tolist()
                    + [0] * self.data_feed.num_tickers,
                    [],
                )
            else:
                # for single stock
                state = (
                    [self.initial_balance]
                    + [self.data.close]
                    + [0] * self.data_feed.num_tickers,
                    [],
                )
        else:
            # Using Previous State
            if len(self.data_feed.data.ticker.unique()) > 1:
                # for multiple stock
                state = (
                    [self.previous_state[0]]
                    + self.data.close.values.tolist()
                    + self.previous_state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ],
                    [],
                )
            else:
                # for single stock
                state = (
                    [self.previous_state[0]]
                    + [self.data.close]
                    + self.previous_state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ],
                    [],
                )
        return state

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def build_observation_space(self):
        pass

    def build_observation(self):
        pass

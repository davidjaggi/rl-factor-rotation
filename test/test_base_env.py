# %%
import random
import unittest

import numpy as np

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.base_env import BaseEnv
from src.utils.load_path import load_data_path

DATA_PATH = load_data_path()
# %%

ENV_CONFIG = {
    "initial_balance": 10000,
    "initial_weights": np.array([0.5, 0.5]),
    "benchmark_type": "custom",
    "benchmark_wgts": np.array([0.5, 0.5]),
    "start_date": "2018-12-31",
    "end_date": "2020-12-31",
    "busday_offset_start": 250,
    "cost_pct": 0.0005,
    "reward_scaling": 1,
    "obs_price_hist": 5,
}


class TestBaseEnv(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.rebalancing_schedule = PeriodicSchedule(frequency="WOM-3FRI")
        self.env = BaseEnv(
            self.feed, config=ENV_CONFIG, rebalance_schedule=self.rebalancing_schedule
        )

    def test_reset(self):
        self.env.reset()
        pass

    def test_step(self):
        self.env.reset()
        action = self.env.action_space.sample()
        obs, rew, done, _ = self.env.step(action)
        pass

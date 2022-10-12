import random
import unittest

import numpy as np

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.portfolio import Portfolio
from src.utils.load_path import load_data_path

DATA_PATH = load_data_path()

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


class TestPortfolio(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.rebalancing_schedule = PeriodicSchedule(frequency="WOM-3FRI")
        self.portfolio = Portfolio([0.5, 0.5], None, "2022-01-01")

    def test_reset(self):
        self.portfolio.reset()
        assert self.portfolio.trade_idx == 0


class TestBenchmarkPortfolio(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.rebalancing_schedule = PeriodicSchedule(frequency="WOM-3FRI")
        self.portfolio = Portfolio([0.5, 0.5], None, "2022-01-01")

    def test_reset(self):
        self.portfolio.reset()
        assert self.portfolio.trade_idx == 0


class TestRLPortfolio(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.rebalancing_schedule = PeriodicSchedule(frequency="WOM-3FRI")
        self.portfolio = Portfolio([0.5, 0.5], None, "2022-01-01")

    def test_reset(self):
        self.portfolio.reset()
        assert self.portfolio.trade_idx == 0

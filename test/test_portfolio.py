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
        test_dict = {
            'name': 'benchmark_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 1000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'schedule': self.rebalancing_schedule,
            'rebalancing_type': 'equally_weigthed'
        }
        self.portfolio = Portfolio(test_dict)

    def test_reset(self):
        prices = self.feed.get_price_data(self.portfolio.start_date)
        self.portfolio.reset(start_date=self.portfolio.start_date, prices=prices)
        assert self.portfolio.trade_idx == 0


class TestBenchmarkPortfolio(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.rebalancing_schedule = PeriodicSchedule(frequency="WOM-3FRI")
        bench_dict = {
            'name': 'benchmark_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 1000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'schedule': self.rebalancing_schedule,
            'rebalancing_type': 'equally_weighted'
        }
        self.portfolio = Portfolio(bench_dict)

    def test_reset(self):
        prices = self.feed.get_price_data(self.portfolio.start_date)
        self.portfolio.reset(start_date=self.portfolio.start_date, prices=prices)
        assert self.portfolio.trade_idx == 0



class TestRLPortfolio(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.rebalancing_schedule = PeriodicSchedule(frequency="WOM-3FRI")
        rl_dict = {
            'name': 'rl_portfolio',
            'initial_positions': 'equally_weighted',
            'initial_balance': 1000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'schedule': self.rebalancing_schedule,
            'rebalancing_type': 'equally_weighted'
        }
        self.portfolio = Portfolio(rl_dict)

    def test_reset(self):
        prices = self.feed.get_price_data(self.portfolio.start_date)
        self.portfolio.reset(start_date=self.portfolio.start_date, prices=prices)
        assert self.portfolio.trade_idx == 0

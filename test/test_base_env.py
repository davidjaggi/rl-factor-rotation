# %%
import random
import unittest

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.base_env import BaseEnv
from src.env.portfolio import BenchmarkPortfolio, RLPortfolio
from src.utils.load_path import load_data_path

DATA_PATH = load_data_path()
# %%

config = {
    'benchmark_portfolio': {
        'name': 'benchmark_portfolio',
        'rebalancing_type': "equally_weighted",
        'initial_balance': 10000,
        'initial_weights': [0.5, 0.5],
        'restrictions': dict(),
        'start_date': '2020-02-24',
        'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
    },
    'rl_portfolio': {
        'name': 'rl_portfolio',
        'rebalancing_type': None,
        'initial_balance': 10000,
        'initial_weights': [0.5, 0.5],
        'restrictions': dict(),
        'start_date': '2020-02-24',
        'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
    },
    'broker': {
        "rl_portfolio": None,
        "benchmark_portfolio": None,
        "start_date": "2018-12-31",
        "end_date": "2020-12-31",
        "busday_offset_start": 250,
        "transaction_cost": 0.0005
    },
    'agent': {
        "reward_scaling": 1,
        "obs_price_hist": 5,
    }
}

# Specify the portfolio configurations
config['broker']['rl_portfolio'] = RLPortfolio(config['rl_portfolio'])
config['broker']['benchmark_portfolio'] = BenchmarkPortfolio(config['benchmark_portfolio'])


class TestBaseEnv(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.env = BaseEnv(config=config, data_feed=self.feed, indicator_pipeline=None)

    def test_reset(self):
        self.env.reset()
        assert self.env.day == 0
        print(self.env.broker)

    def test_step(self):
        self.env.reset()
        action = self.env.action_space.sample()
        obs, rew, done, _ = self.env.step(action)
        assert done == False
        assert action == 0
        assert rew == 100

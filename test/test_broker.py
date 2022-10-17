import random
import unittest

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.broker import Broker
from src.env.portfolio import BenchmarkPortfolio, RLPortfolio
from src.utils.load_path import load_data_path

DATA_PATH = load_data_path()

class TestBroker(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(1)
        self.feed = CSVDataFeed(
            DATA_PATH + "/example_data.csv"
        )
        self.rebalancing_schedule = PeriodicSchedule(frequency="WOM-3FRI")

        bench_config = {
            'name': 'benchmark_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 10000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'schedule': self.rebalancing_schedule,
            'rebalancing_type': "equally_weighted"
        }

        rl_config = {
            'name': 'rl_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 10000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'schedule': self.rebalancing_schedule,
            'rebalancing_type': "equally_weighted"
        }

        broker_config = {
            "rl_portfolio": RLPortfolio(rl_config),
            "benchmark_portfolio": BenchmarkPortfolio(bench_config),
            "start_date": "2018-12-31",
            "end_date": "2020-12-31",
            "busday_offset_start": 250,
            "transaction_cost": 0.0005,
            "reward_scaling": 1,
            "obs_price_hist": 5,
        }
        self.broker = Broker(self.feed, broker_config)

    def test_reset(self,):
        bench_config = {
            'name': 'benchmark_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 10000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'schedule': self.rebalancing_schedule,
            'rebalancing_type': 'equally_weigthed'
        }

        self.broker.reset(BenchmarkPortfolio(bench_config))

        rl_config = {
            'name': 'rl_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 10000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'schedule': self.rebalancing_schedule,
            'rebalancing_type': 'equally_weigthed',
        }

        self.broker.reset(RLPortfolio(rl_config))

        pass

    def test_initial_weights(self):
        pass

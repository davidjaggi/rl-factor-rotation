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
            file_name=DATA_PATH + "/example_data.csv", start_date='2020-02-24'
        )

        bench_config = {
            'name': 'benchmark_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 10000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'end_date': '2020-12-31',
            'rebalancing_type': "equally_weighted"
        }
        bench_config['rebalancing_schedule'] = PeriodicSchedule(frequency="WOM-3FRI",
                                                                start_date=bench_config['start_date'],
                                                                end_date=bench_config['end_date'])

        rl_config = {'name': 'rl_portfolio', 'initial_positions': "equally_weighted", 'initial_balance': 10000,
                     'initial_weights': [0.5, 0.5], 'restrictions': dict(), 'start_date': '2020-02-24',
                     'end_date': '2020-12-31', 'rebalancing_type': "equally_weighted",
                     'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI",
                                                              start_date=bench_config['start_date'],
                                                              end_date=bench_config['end_date'])}

        broker_config = {
            "rl_portfolio": RLPortfolio(rl_config),
            "benchmark_portfolio": BenchmarkPortfolio(bench_config),
            "busday_offset_start": 250,
            "transaction_cost": 0.0005,
            "reward_scaling": 1,
            "obs_price_hist": 5,
        }
        self.broker = Broker(self.feed, broker_config)

    def test_reset(self, ):
        bench_config = {
            'name': 'benchmark_portfolio',
            'initial_positions': "equally_weighted",
            'initial_balance': 10000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'start_date': '2020-02-24',
            'end_date': '2020-12-31',
            'rebalancing_type': 'equally_weighted'
        }
        bench_config['rebalancing_schedule'] = PeriodicSchedule(frequency="WOM-3FRI",
                                                                start_date=bench_config['start_date'],
                                                                end_date=bench_config['end_date'])
        benchmark_portfolio = BenchmarkPortfolio(bench_config)
        self.broker.reset(
            benchmark_portfolio)  # This works as inteded now, but when implementing the reset in the Env,
        # the portfolio should be a self.broker.(Bm/rl)_portfolio

        rl_config = {'name': 'rl_portfolio', 'initial_positions': "equally_weighted", 'initial_balance': 10000,
                     'initial_weights': [0.5, 0.5], 'restrictions': dict(), 'start_date': '2020-02-24',
                     'end_date': '2020-12-31', 'rebalancing_type': 'equally_weighted',
                     'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI",
                                                              start_date=bench_config['start_date'],
                                                              end_date=bench_config['end_date'])}
        rl_portfolio = RLPortfolio(rl_config)
        self.broker.reset(rl_portfolio)

        pass

    def test_initial_weights(self):
        pass

    def test_rebalance(self):
        pass


if __name__ == '__main__':
    unittest.main()

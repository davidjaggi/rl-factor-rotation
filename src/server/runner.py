# %%
import random

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.base_env import BaseEnv
from src.env.portfolio import BenchmarkPortfolio, RLPortfolio
from src.utils.load_path import load_data_path

DATA_PATH = load_data_path()
# %%

def ret(days, initial_balance, start_date, end_date, transaction_cost, reward_scaling, obs_price_hist, weighting_method, training_data):
    config = {
        'benchmark_portfolio': {
            'name': 'benchmark_portfolio',
            'rebalancing_type': weighting_method,
            'investment_universe': ["GOOGL.O", "AAPL.O"],
            'initial_balance': int(initial_balance),
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
        },
        'rl_portfolio': {
            'name': 'rl_portfolio',
            'rebalancing_type': None,
            'investment_universe': ["GOOGL.O", "AAPL.O"],
            'initial_balance': int(initial_balance),
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
        },
        'broker': {
            "rl_portfolio": None,
            "benchmark_portfolio": None,
            "start_date": start_date,
            "end_date": end_date,
            "busday_offset_start": 250,
            "transaction_cost": transaction_cost
        },
        'agent': {
            "reward_scaling": int(reward_scaling),
            "obs_price_hist": int(obs_price_hist),
        }
    }

    # Specify the portfolio configurations
    config['broker']['rl_portfolio'] = RLPortfolio(config['rl_portfolio'])
    config['broker']['benchmark_portfolio'] = BenchmarkPortfolio(config['benchmark_portfolio'])

    # %%
    random.seed(1)
    feed = CSVDataFeed(
        DATA_PATH + training_data
    )
    env = BaseEnv(config=config, data_feed=feed, indicator_pipeline=[])

    env.reset()
    for i in range(int(days)):
        action = env.action_space.sample()
        obs, rew, done, _ = env.step(action)

    # return the environment
    return env

# %%
import random


from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.base_env import BaseEnv
from src.env.portfolio import BenchmarkPortfolio, RLPortfolio
from src.utils.load_path import load_data_path
from src.env.plotting import pltt

DATA_PATH = load_data_path()
# %%


def ret(days):
    config = {
        'benchmark_portfolio': {
            'name': 'benchmark_portfolio',
            'rebalancing_type': "equally_weighted",
            'investment_universe': ["GOOGL.O", "AAPL.O"],
            'initial_balance': 100000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
            'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
        },
        'rl_portfolio': {
            'name': 'rl_portfolio',
            'rebalancing_type': None,
            'investment_universe': ["GOOGL.O", "AAPL.O"],
            'initial_balance': 100000,
            'initial_weights': [0.5, 0.5],
            'restrictions': dict(),
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

    # %%
    random.seed(1)
    feed = CSVDataFeed(
        DATA_PATH + "/example_data.csv"
    )
    env = BaseEnv(config=config, data_feed=feed, indicator_pipeline=[])

    env.reset()
    for i in range(int(days)):
        print(env.day)
        print(env.date)
        action = env.action_space.sample()
        obs, rew, done, _ = env.step(action)

# %%

    return env.broker.hist_dict

#res_bm, res_rl = pltt() # placeholder because simulating data

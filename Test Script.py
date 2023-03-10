# %%
from datetime import date

from src.analyzer.analyzer import Analyzer
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
        'investment_universe': ["MKT_Index", "SMB_Index", 'HML_Index', 'RF_Index'],
        'initial_balance': int(10000),
        'initial_weights': [0.25, 0.25, 0.25, 0.25],
        'restrictions': {"direction": "long_only"},
        'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
    },
    'rl_portfolio': {
        'name': 'rl_portfolio',
        'rebalancing_type': None,
        'investment_universe': ["MKT_Index", "SMB_Index", 'HML_Index', 'RF_Index'],
        'initial_balance': int(10000),
        'initial_weights': [0.25, 0.25, 0.25, 0.25],
        'restrictions': {"direction": "long_only"},

        'rebalancing_schedule': PeriodicSchedule(frequency="WOM-3FRI")
    },
    'broker': {
        "rl_portfolio": None,
        "benchmark_portfolio": None,
        "start_date": date(2000, 12, 31),
        "end_date": date(2020, 12, 31),
        "busday_offset_start": 250,
        "transaction_cost": 0.05
    },
    'agent': {
        "reward_scaling": int(1),
        "obs_price_hist": int(250),
    }
}

# Specify the portfolio configurations
config['broker']['rl_portfolio'] = RLPortfolio(config['rl_portfolio'])
config['broker']['benchmark_portfolio'] = BenchmarkPortfolio(config['benchmark_portfolio'])

# random.seed(1)
feed = CSVDataFeed(
    DATA_PATH + "/example_factor_clean.csv",
)
env = BaseEnv(config=config, data_feed=feed)

env.reset()
done = False
while not done:
    action = env.action_space.sample()
    obs, rew, done, _ = env.step(action)

# %%
analyzer = Analyzer(env)
# %%
df = analyzer.data
# %%
analyzer.get_prices()
# %%
analyzer.get_cash("rl")
# %%
analyzer.get_rewards()

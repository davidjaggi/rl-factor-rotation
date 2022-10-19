from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.portfolio import BenchmarkPortfolio, RLPortfolio

config = {
    'benchmark_portfolio': {
        'name': 'benchmark_portfolio',
        'type': "equally_weighted",
        'initial_balance': 10000,
        'initial_weights': [0.5, 0.5],
        'restrictions': dict(),
        'start_date': '2020-02-24',
        'schedule': PeriodicSchedule(frequency="WOM-3FRI")
    },
    'rl_portfolio': {
        'name': 'rl_portfolio',
        'type': None,
        'initial_balance': 10000,
        'initial_weights': [0.5, 0.5],
        'restrictions': dict(),
        'start_date': '2020-02-24',
        'schedule': PeriodicSchedule(frequency="WOM-3FRI")
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

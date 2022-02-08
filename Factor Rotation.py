# %%
import numpy as np
from src.data.data_feed import DataFeed
from src.environment import TradingEnvironment

from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines import DQN
# %%
# Input parameters
START_DATE = '2020-01-02'               # start date of simulation
END_DATE = '2020-12-31'                 # end date of simulation
initial_balance = 10000                 # cash to be invested
benchmark_wgts = np.array([0.5, 0.5])   # benchmark weights

n_sample = 252                          # number of dates to be generated
dt = 1 / 252                            # time delta
# %%
data_feed = DataFeed(["AAPL","MSFT"], START_DATE, END_DATE)
# %%
trading_env = TradingEnvironment(data_feed, initial_balance)
# %%
model = 
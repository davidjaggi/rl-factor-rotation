# %%
import numpy as np
from src.data.data_feed import BaseDataFeed
from src.environment import BaseEnvironment

# %%
# Input parameters
START_DATE = '2020-01-02'               # start date of simulation
END_DATE = '2020-12-31'                 # end date of simulation
initial_balance = 10000                 # cash to be invested
benchmark_wgts = np.array([0.5, 0.5])   # benchmark weights

n_sample = 252                          # number of dates to be generated
dt = 1 / 252                            # time delta
# %%
data_feed = BaseDataFeed(["AAPL","MSFT"], START_DATE, END_DATE)
# %%
trading_env = BaseEnvironment(data_feed, initial_balance)
# %%
model = 
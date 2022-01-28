# %%
import gym
from gym.utils import seeding
import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data
import random
import os

from src.core.data import generate_paths
from src.core.environment.portfolio_environment import PortfolioEnvironment
# %%
# Input parameters
START_DATE = '2020-01-02'               # start date of simulation
END_DATE = '2020-12-31'                 # end date of simulation
initial_balance = 10000                 # cash to be invested
benchmark_wgts = np.array([0.5, 0.5])   # benchmark weights

spot = np.array([100, 100])             # start prices for simulation
drift = np.array([0.1, -0.1])           # drift parameters
sigma = np.array([0.1, 0.1])            # volatility
correlation = np.array([[1.0, 0.8], [0.8, 1.0]])  # correlation matrix
n_sample = 252                          # number of dates to be generated
dt = 1 / 252                            # time delta

# %%
path_generator = lambda: generate_paths(spot, drift, sigma, correlation, START_DATE, END_DATE, dt)
rebalancing_dates = pd.date_range(START_DATE, END_DATE, freq='WOM-3FRI')

# %%
paths = path_generator()
#paths.plot()

# %%
ptf_env = PortfolioEnvironment(path_generator, initial_balance, rebalancing_dates, benchmark_wgts)

# %%
from stable_baselines.common.policies import MlpPolicy
# import MlpPolicy

from stable_baselines import DQN

# %%
model = DQN(MlpPolicy, ptf_env, verbose=1, tensorboard_log="logs")
# %%
model.learn(total_timesteps=6000)

# %%
rewards = []
episodes = 100

for _ in range(episodes):
    state = ptf_env.reset()
    cum_reward = 0

    done = False
    while not done:
        action, _ = model.predict(state)
        state, reward, done, info = ptf_env.step(action)
        cum_reward += reward
    # ptf_env.render()
    rewards.append(cum_reward)

plt.plot(rewards)

# %%
rewards = []
episodes = 3

for _ in range(episodes):
    state = ptf_env.reset()
    cum_reward = 0
    done = False
    while not done:
        action, _ = model.predict(state)
        state, reward, done, info = ptf_env.step(action)
        cum_reward += reward
    ptf_env.render()
    rewards.append(cum_reward)
# %%
from tensorboard import notebook
notebook.list()
# %%
notebook.display(port=6006, height=1000)
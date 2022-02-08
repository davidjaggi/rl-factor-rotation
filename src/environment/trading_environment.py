# %%
import numpy as np
import gym
from gym.utils import seeding
import pandas as pd
import matplotlib.pyplot as plt
import itertools

from src.environment import backtest_from_to

# %%
class TradingEnvironment(gym.Env):
    def __init__(self, data_feed, starting_value, split_weight=10, lookback_win=6):
        """ Initialises the class """

        self.data_feed = data_feed
        self.starting_value = starting_value
        self.weight_increments = 1/split_weight
        self.lookback_win = lookback_win

        self.action_space = gym.spaces.Discrete(split_weight+1)
        self.observation_space = gym.spaces.Discrete(8)

        self.seed()

    def reset(self):
        """ Reset the environment to the initial state """

        if isinstance(self.data_feed.data, pd.DataFrame):
            self.data = self.data_feed.data
        else:
            self.data = self.data_feed().data

        self.time_step = 0
        self.reward = 0
        self.p_and_l = pd.DataFrame(columns=['P&L'])
        self.p_and_l_bmk = pd.DataFrame(columns=['P&L_Bmk'])
        self.ptf_value = self.starting_value
        self.ptf_value_bmk = self.starting_value
        self.done = False
        self.state = self.convert_obs(self.data.loc[:self.rebalancing[0]], 0)

        return self.state

    def step(self, action):
        """ Performs an interaction step within the environment, given an action """

        # rescale action to weights in both assets
        action_converted = self.weight_increments * action
        action = np.append(action_converted, np.array([1 - action_converted]))

        # if we reached the final rebalancing date, the next date is just the last available date
        if self.time_step == len(self.rebalancing) - 1:
            self.done = True
            next_date = self.data.index[-1]
        else:
            next_date = self.rebalancing[self.time_step + 1]
        date = self.rebalancing[self.time_step]

        # backtest both the strategy as well as the benchmark until next rebalancing date
        p_and_l, cash = backtest_from_to(action, self.data, date, next_date, self.ptf_value)
        p_and_l_bmk, cash_bmk = backtest_from_to(self.benchmark_wgts,
                                                 self.data, date, next_date, self.ptf_value_bmk)

        # rename the P&L values and attached to the dataframes
        p_and_l.columns = self.p_and_l.columns.to_list()
        p_and_l_bmk.columns = self.p_and_l_bmk.columns.to_list()
        self.p_and_l = self.p_and_l.append(p_and_l)
        self.p_and_l_bmk = self.p_and_l_bmk.append(p_and_l_bmk)

        # define the reward
        self.reward += (self.p_and_l.values[-1][0] + cash) / self.ptf_value - \
                       (self.p_and_l_bmk.values[-1][0] + cash_bmk) / self.ptf_value_bmk

        # update the portfolio values with new performance
        self.ptf_value = self.p_and_l.values[-1][0] + cash
        self.ptf_value_bmk = self.p_and_l_bmk.values[-1][0] + cash_bmk

        # define the next state
        self.state = self.convert_obs(self.data.loc[:next_date], self.ptf_value / self.ptf_value_bmk - 1)

        # increase time step since step has been performed
        self.time_step += 1

        return self.state, self.reward, self.done, {}

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def convert_obs(self, obs_raw, extra_value):
        """ defines how observations should look like  """

        # convert 'lookback_win' return to binary
        look_back = self.lookback_win
        if len(obs_raw) < look_back:
            look_back = len(obs_raw)
        rets = (obs_raw.iloc[-1, :] / obs_raw.iloc[-look_back, :] - 1).values
        rets[rets > 0] = 1
        rets[rets <= 0] = 0

        # convert reward to binary
        if extra_value > 0:
            extra_value = 1
        else:
            extra_value = 0

        # convert binaries to integer within observation space
        possible_1 = possible_2 = possible_r = [0, 1]
        combs = list(itertools.product(possible_1, possible_2, possible_r))
        obs_converted = combs.index((rets[0], rets[1], extra_value))

        return obs_converted

    def render(self, mode='human'):
        """ used for plotting the environment state  """

        pd.concat([self.p_and_l, self.p_and_l_bmk], axis=1).plot()
        plt.show(block=False)
        plt.pause(0.5)
        if self.done:
            input("Press Enter to continue...")
        plt.close('all')
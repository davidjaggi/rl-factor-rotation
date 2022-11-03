from abc import ABC

import gym
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gym.utils import seeding

from src.env.broker import Broker
from src.env.portfolio import BenchmarkPortfolio, RLPortfolio


class BaseEnv(gym.Env, ABC):
    """
    Base class for all trading environments.
    """

    def __init__(
            self, config=None, data_feed=None, indicator_pipeline=[]):
        """Initialises the class"""
        self.config = config
        self.data_feed = data_feed
        self.indicator_pipeline = indicator_pipeline

        # self.observation_space = self.build_observation_space()
        self.action_space = self.build_action_space()

        # initialize the broker and the portfolios
        self.broker = Broker(config=self.config["broker"], data_feed=self.data_feed)
        self.rl_portfolio = RLPortfolio(self.config["rl_portfolio"])
        self.benchmark_portfolio = BenchmarkPortfolio(self.config["benchmark_portfolio"])

        self.reward_scaling = self.config['agent']["reward_scaling"]
        self.obs_price_hist = self.config['agent']["obs_price_hist"]

        self._seed()

    def reset(self):
        """Resets the environment to its initial state"""

        self.done = False

        # initialize reward
        self.date = self.config["broker"]["start_date"]
        self.day = self.data_feed.get_idx(self.date)
        self.reward = 0
        self.cost = 0
        self.trades = 0
        self.episode = 0

        # memorize changes
        self.rewards_memory = []
        self.actions_memory = []

        # reset the portfolios
        self.broker.reset(self.rl_portfolio, self.day)
        self.broker.reset(self.benchmark_portfolio, self.day)
        # initialize state
        self.state = self.build_observation()
        # return self.state

    def build_observation(self):

        prices = self.data_feed.get_observations(self.day, offset=self.obs_price_hist)
        # create observation space with prices and indicators
        obs = prices
        if self.indicator_pipeline is not None:
            # this will have to be built first
            if len(self.indicator_pipeline) > 0:
                for indicator in self.indicator_pipeline.indicators:
                    inds = indicator.calc()
                    obs = np.append(obs, inds, axis=0)
        # obs = np.append(obs, self.current_holdings)  # attach current holdings # TODO add current holdings
        # obs = np.append(obs, self.asset_memory[-1])  # attach last portfolio value # TODO add last portfolio value

        return obs

    def step(self, actions):
        assert self.done is False, "reset() must be called before step()"
        # transform actions to units
        self.actions_memory.append(actions)
        delta = self.actions_to_ideal_weights_delta(self.rl_portfolio, actions)

        self.broker.update_ideal_weights(self.rl_portfolio, delta)
        # execute trades
        dt, prices = self.data_feed.get_prices_snapshot(idx=self.day)
        self.broker.rebalance(dt, prices, self.rl_portfolio)
        self.broker.rebalance(dt, prices, self.benchmark_portfolio)

        self.reward = self.reward_func()
        self.reward = self.reward * self.reward_scaling  # scale reward
        self.rewards_memory.append(self.reward)

        # state: s -> s+1
        self.day += 1
        self.state = self.build_observation()
        self.done = self.day >= len(self.data_feed.dates) - 1

        return self.state, self.reward, self.done, {}

    def actions_to_ideal_weights_delta(self, portfolio, actions):
        """Converts actions to portfolio weights
        # TODO: make the trade factor configurable
        The current setup normalizes the weights to sum to 1."""
        n_assets = len(portfolio.investment_universe)

        if actions == 0:
            delta = {asset: 0 for asset in portfolio.investment_universe}
        else:
            delta = {asset: -0.05 / (n_assets - 1) for asset in portfolio.investment_universe}
            delta[portfolio.investment_universe[actions - 1]] = 0.05
        return delta

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _benchmark_weights(self):
        # TODO: make this a function of the broker
        if self.config["benchmark_type"] == "equally_weighted":
            wgts = np.ones(self.data_feed.num_assets) / self.data_feed.num_assets
        elif self.config["benchmark_type"] == "custom":
            wgts = self.config["benchmark_wgts"]
        else:
            raise ValueError("Benchmark type not known yet!")
        return wgts

    @property
    def bmk_performance(self):
        if self.config["benchmark_type"] is not None:
            df = pd.DataFrame(
                list(zip(self.date_memory, self.bmk_memory)),
                columns=["Date", "Bmk_Value"],
            )
            df = df.set_index("Date")
        else:
            df = pd.DataFrame(columns=["Bmk_Value"])
        return df

    @property
    def ptf_performance(self):
        # TODO: make this a fuction of the portfolio
        df = pd.DataFrame(
            list(zip(self.date_memory, self.asset_memory)),
            columns=["Date", "Ptf_Value"],
        )
        df = df.set_index("Date")
        return df

    def plot_current_performance(self):
        # TODO: make this a fuction of the portfolio
        """Plot current performance of the agent"""
        if self.config["benchmark_type"] is not None:
            dfs = pd.concat([self.bmk_performance, self.ptf_performance], axis=1)
        else:
            dfs = self.ptf_performance
        plt.plot(dfs)
        plt.title("Portfolio Performance")
        plt.legend(dfs.columns)
        plt.show()

    def plot_rewards(self):
        """Plot the rewards over time"""
        plt.plot(self.rewards_memory)
        plt.title("Rewards")
        plt.show()

    def plot_actions(self):
        """Plot the rewards over time"""
        plt.plot(self.actions_memory)
        plt.title("Actions")
        plt.show()

    def build_observation_space(self):
        """Builds the observation space"""
        return gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            # TODO get the number of assets from the broker class
            shape=(
                self.config["obs_price_hist"] * 2
                + 2
                + 1,
            ),
            dtype=np.float64
        )

    def build_action_space(self):
        # return three discrete action
        # action 0 do nothing
        # action 1 buy asset 1
        # action 2 buy asset 2
        return gym.spaces.Discrete(3)

    def reward_func(self):
        """Reward function for the portfolio. Currently the distance of the portfolio to the benchmark."""
        # TODO: implement correct reward function
        reward = 100
        return reward

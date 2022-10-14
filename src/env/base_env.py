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
            self, config=None, data_feed=None, indicator_pipeline=None
    ):
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

        # set start and end date as well as rebalancing periods...
        # if isinstance(self.rebalance_schedule, list):
        #     self.start_date = self.rebalance_schedule[0].strftime("%Y-%m-%d")
        #     self.end_date = self.rebalance_schedule[-1].strftime("%Y-%m-%d")
        #     self.rebalance_periods = self.rebalance_schedule
        # else:
        #     self.start_date = self.config["start_date"]
        #     self.end_date = self.config["end_date"]
        #
        # self.data_feed.reset_feed(
        #     start_dt=(
        #             pd.to_datetime(self.start_date)
        #             - timedelta(days=self.config["busday_offset_start"])
        #     ).strftime("%Y-%m-%d"),
        #     end_dt=self.end_date,
        # )
        # if self.rebalance_schedule is None:
        #     self.rebalance_periods = [
        #         idx
        #         for idx in self.data_feed.get_data_idx()
        #         if idx >= pd.to_datetime(self.start_date)
        #     ]
        # if isinstance(self.rebalance_schedule, RebalancingSchedule):
        #     self.rebalance_schedule.set_start_and_end(
        #         start_date=self.start_date, end_date=self.end_date
        #     )
        #     schedule = self.rebalance_schedule.schedule()
        #     self.rebalance_periods = schedule
        self._seed()

    def reset(self):
        """Resets the environment to its initial state"""

        self.terminal = False

        # initialize reward
        self.day = 0
        self.reward = 0
        self.cost = 0
        self.trades = 0
        self.episode = 0
        # self.current_holdings = np.zeros(self.data_feed.num_assets)
        # self.current_weights = self.config["initial_weights"]
        # self.current_holdings_bmk = np.zeros(self.data_feed.num_assets)

        # memorize changes
        # self.asset_memory = [self.initial_balance]
        # self.bmk_memory = [self.initial_balance]
        # self.date_memory = [self.rebalance_periods[0]]
        self.rewards_memory = []
        self.actions_memory = []
        self.weights_memory = []
        self.trades_memory = []

        # reset broker
        self.broker.reset(self.benchmark_portfolio)
        # initialize state
        # self.state = self.build_observation(self.rebalance_periods[self.day])
        # return self.state

    def build_observation(self, date):
        """ Builds the observation space """
        obs = np.empty((0, self.data_feed.num_assets), np.float)
        if self.indicator_pipeline is not None:
            # this will have to be built first
            for indicator in self.indicator_pipeline.indicators:
                inds = indicator.calc()
                obs = np.append(obs, inds, axis=0)
        prices = self.data_feed.get_price_data(date, offset=self.obs_price_hist)
        obs = np.append(obs, prices.to_numpy(dtype=np.float), axis=0).flatten(order="F")
        obs = np.append(obs, self.current_holdings)  # attach current holdings
        obs = np.append(obs, self.asset_memory[-1])  # attach last portfolio value
        return obs

    def step(self, actions):
        assert self.terminal is False, "reset() must be called before step()"

        self.current_prices = self.data_feed.get_price_data(
            end_dt=self.rebalance_periods[self.day + 1],
            start_dt=self.rebalance_periods[self.day],
        )
        self.current_returns = self.data_feed.get_returns_data(
            end_dt=self.rebalance_periods[self.day + 1],
            start_dt=self.rebalance_periods[self.day],
        )
        # transform actions to units
        actions = self._convert_action(actions)
        self.actions_memory.append(actions)
        trades = self.actions_to_trades(actions)
        wgts, units, costs = self.weights_to_shares(
            trades, self.current_weights, self.asset_memory[-1], self.current_holdings
        )
        self.current_weights = wgts
        self.current_holdings = units
        self.current_ptf_values = np.sum(
            units * self.current_prices.iloc[1:, :].to_numpy(), axis=1
        )
        self.asset_memory.extend(self.current_ptf_values.tolist())

        # do the same with a benchmark if there is one...
        if self.config["benchmark_type"] is not None:
            wgts_bmk = self._benchmark_weights()
            wgts_bmk, units_bmk, costs_bmk = self.weights_to_shares(
                None, wgts_bmk, self.bmk_memory[-1], self.current_holdings_bmk
            )
            self.current_holdings_bmk = units_bmk
            self.current_ptf_values_bmk = np.sum(
                units_bmk * self.current_prices.iloc[1:, :].to_numpy(), axis=1
            )
            self.bmk_memory.extend(self.current_ptf_values_bmk.tolist())

        self.date_memory.extend([dt for dt in self.current_prices.index[1:]])

        self.reward = self.reward_func()
        self.reward = self.reward * self.reward_scaling  # scale reward
        self.rewards_memory.append(self.reward)
        self.weights_memory.append(wgts)
        self.trades_memory.append(trades)

        # state: s -> s+1
        self.day += 1
        self.state = self.build_observation(self.rebalance_periods[self.day])
        self.terminal = self.day >= len(self.rebalance_periods) - 1

        return self.state, self.reward, self.terminal, {}

    def _convert_action(self, action):
        """Used if actions need to be transformed without having to change entire step() method"""
        # let's convert the actions so the one with the higher value is bought and the other is sold
        action = action - 1
        return action

    def actions_to_trades(self, actions):
        """Converts actions to portfolio weights
        # TODO: make the trade factor configurable
        The current setup normalizes the weights to sum to 1."""
        # action -1 is sell 5 % of asset 1
        # action 0 is hold both assets
        # action 1 is buy 5% of asset 1
        if actions == -1:
            return np.array([-0.05, 0.05])
        elif actions == 0:
            return np.zeros(2)
        elif actions == 1:
            return np.array([0.05, -0.05])
        else:
            raise ValueError("Invalid action: {}".format(actions))


    def weights_to_shares(self, trades, current_weights, current_val, current_holding):
        """Logic for transforming raw actions into number of shares for each asset"""
        asset_prices = self.current_prices.iloc[0, :].to_numpy()
        if trades is None:
            new_weights = current_weights
        else:
            new_weights = np.add(trades, current_weights)
            # normalize weights
            new_weights = new_weights / np.sum(new_weights)

        asset_values = new_weights * current_val
        units_gross = asset_values / asset_prices
        costs = (
                np.abs(units_gross - current_holding)
                * asset_prices
                * self.cost_pct
        )
        units_net = (asset_values - costs) / asset_prices
        weights = (units_net * asset_prices) / np.sum(units_net * asset_prices)
        return weights, units_net, np.sum(costs)

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _benchmark_weights(self):
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
        df = pd.DataFrame(
            list(zip(self.date_memory, self.asset_memory)),
            columns=["Date", "Ptf_Value"],
        )
        df = df.set_index("Date")
        return df

    def plot_current_performance(self):
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
        reward = self.current_ptf_values[-1] - self.current_ptf_values_bmk[-1]
        return reward

# if __name__ == "__main__":
#     from src.data.rebalancing_schedule import PeriodicSchedule
#     from src.data.feed import CSVDataFeed
#     import matplotlib.pyplot as plt
#
#     feed = CSVDataFeed(file_name="../../data/example_data.csv")
#
#     ENV_CONFIG = {
#         "initial_balance": 10000,
#         "initial_weights": np.array([0.5, 0.5]),
#         "benchmark_type": "custom",
#         "benchmark_wgts": np.array([0.5, 0.5]),
#         "start_date": "2018-12-31",
#         "end_date": "2020-12-31",
#         "busday_offset_start": 250,
#         "cost_pct": 0.0005,
#         "reward_scaling": 1,
#         "obs_price_hist": 5,
#     }
#
#     # now try a different rebalancing frequency...
#     schedule = PeriodicSchedule(frequency="WOM-3FRI")
#
#     env = BaseEnv(data_feed=feed, config=ENV_CONFIG, rebalance_schedule=schedule)
#     obs = env.reset()
#     done = False
#     while not done:
#         # implement simple agent
#         action = env.action_space.sample()
#         obs, rew, done, _ = env.step(action)
#     env.plot_current_performance()
#     plt.show()

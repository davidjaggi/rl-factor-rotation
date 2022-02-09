# %%
# this script is heavitly based on the work of FinRL
# https://github.com/AI4Finance-Foundation/FinRL/blob/master/finrl/finrl_meta/env_stock_trading/env_stocktrading.py
# %%
import numpy as np
import gym
from gym.utils import seeding
import pandas as pd
import matplotlib.pyplot as plt
import itertools

# %%
BASE_CONFIG = {
    "portfolio_config": {"initial_balance": 10000},
    "benchmark_config": {"type": "equally_weighted"},
}

# %%
class BaseEnvironment(gym.Env):
    def __init__(self, data_feed, config, action_space):
        """Initialises the class"""
        self.time = 0
        self.hmax = 100
        self.buy_cost_pct = 0.005
        self.sell_cost_pct = 0.005
        self.data_feed = data_feed
        self.data = self.data_feed.data
        self.config = BASE_CONFIG | config
        self.action_space = action_space
        self.observation_space = self.build_observation_space()

        self.initial_balance = self.config["portfolio_config"]["initial_balance"]

        self.initial = True
        self.terminal = False
        # initialize state
        self.state = self._initiate_state()

        # initialize reward
        self.reward = 0
        self.cost = 0
        self.trades = 0
        self.episode = 0

        # memorize changes
        self.asset_memory = [self.initial_balance]
        self.rewards_memory = []
        self.actions_memory = []
        self.date_memory = [self._get_date()]
        self.reward_scaling = 1
        # self.reset()
        self._seed()

    def reset(self):
        # initialize state
        self.state = self._initiate_state()

        if self.initial:
            self.asset_memory = [self.initial_balance]
        else:
            previous_total_asset = self.previous_state[0] + sum(
                np.array(self.state[1 : (self.data_feed.num_tickers + 1)])
                * np.array(
                    self.previous_state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
            )
            self.asset_memory = [previous_total_asset]

        self.initial_balance = self.config["portfolio_config"]["initial_balance"]
        self.reward = 0
        self.done = False
        self.state = self.build_observation()

    def _sell(self, index, action):
        def _do_sell():
            if self.state[index + 1] > 0:
                # Sell only if the price is > 0 (no missing data in this particular date)
                # perform sell action based on the sign of the action
                if self.state[index + self.data_feed.num_tickers + 1] > 0:
                    # Sell only if current asset is > 0
                    sell_num_shares = min(
                        abs(action), self.state[index + self.data_feed.num_tickers + 1]
                    )
                    sell_amount = (
                        self.state[index + 1]
                        * sell_num_shares
                        * (1 - self.sell_cost_pct)
                    )
                    # update balance
                    self.state[0] += sell_amount

                    self.state[
                        index + self.data_feed.num_tickers + 1
                    ] -= sell_num_shares
                    self.cost += (
                        self.state[index + 1] * sell_num_shares * self.sell_cost_pct
                    )
                    self.trades += 1
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = 0

            return sell_num_shares

        sell_num_shares = _do_sell()

        return sell_num_shares

    def _buy(self, index, action):
        def _do_buy():
            if self.state[index + 1] > 0:
                # Buy only if the price is > 0 (no missing data in this particular date)
                available_amount = self.state[0] // self.state[index + 1]
                # print('available_amount:{}'.format(available_amount))

                # update balance
                buy_num_shares = min(available_amount, action)
                buy_amount = (
                    self.state[index + 1] * buy_num_shares * (1 + self.buy_cost_pct)
                )
                self.state[0] -= buy_amount

                self.state[index + self.data_feed.num_tickers + 1] += buy_num_shares

                self.cost += self.state[index + 1] * buy_num_shares * self.buy_cost_pct
                self.trades += 1
            else:
                buy_num_shares = 0

            return buy_num_shares

        buy_num_shares = _do_buy()

        return buy_num_shares

    def step(self, actions):
        self.terminal = self.time >= len(self.data.index.unique()) - 1
        if self.terminal:
            # print(f"Episode: {self.episode}")
            if self.make_plots:
                self._make_plot()
            end_total_asset = self.state[0] + sum(
                np.array(self.state[1 : (self.data_feed.num_tickers + 1)])
                * np.array(
                    self.state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
            )
            df_total_value = pd.DataFrame(self.asset_memory)
            tot_reward = (
                self.state[0]
                + sum(
                    np.array(self.state[1 : (self.data_feed.num_tickers + 1)])
                    * np.array(
                        self.state[
                            (self.data_feed.num_tickers + 1) : (
                                self.data_feed.num_tickers * 2 + 1
                            )
                        ]
                    )
                )
                - self.initial_amount
            )
            df_total_value.columns = ["account_value"]
            df_total_value["date"] = self.date_memory
            df_total_value["daily_return"] = df_total_value["account_value"].pct_change(
                1
            )
            if df_total_value["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_total_value["daily_return"].mean()
                    / df_total_value["daily_return"].std()
                )
            df_rewards = pd.DataFrame(self.rewards_memory)
            df_rewards.columns = ["account_rewards"]
            df_rewards["date"] = self.date_memory[:-1]
            if self.episode % self.print_verbosity == 0:
                print(f"day: {self.time}, episode: {self.episode}")
                print(f"begin_total_asset: {self.asset_memory[0]:0.2f}")
                print(f"end_total_asset: {end_total_asset:0.2f}")
                print(f"total_reward: {tot_reward:0.2f}")
                print(f"total_cost: {self.cost:0.2f}")
                print(f"total_trades: {self.trades}")
                if df_total_value["daily_return"].std() != 0:
                    print(f"Sharpe: {sharpe:0.3f}")
                print("=================================")

            if (self.model_name != "") and (self.mode != ""):
                df_actions = self.save_action_memory()
                df_actions.to_csv(
                    "results/actions_{}_{}_{}.csv".format(
                        self.mode, self.model_name, self.iteration
                    )
                )
                df_total_value.to_csv(
                    "results/account_value_{}_{}_{}.csv".format(
                        self.mode, self.model_name, self.iteration
                    ),
                    index=False,
                )
                df_rewards.to_csv(
                    "results/account_rewards_{}_{}_{}.csv".format(
                        self.mode, self.model_name, self.iteration
                    ),
                    index=False,
                )
                plt.plot(self.asset_memory, "r")
                plt.savefig(
                    "results/account_value_{}_{}_{}.png".format(
                        self.mode, self.model_name, self.iteration
                    ),
                    index=False,
                )
                plt.close()

            # Add outputs to logger interface
            # logger.record("environment/portfolio_value", end_total_asset)
            # logger.record("environment/total_reward", tot_reward)
            # logger.record("environment/total_reward_pct", (tot_reward / (end_total_asset - tot_reward)) * 100)
            # logger.record("environment/total_cost", self.cost)
            # logger.record("environment/total_trades", self.trades)

            return self.state, self.reward, self.terminal, {}

        else:
            actions = actions * self.hmax  # actions initially is scaled between 0 to 1
            actions = actions.astype(
                int
            )  # convert into integer because we can't by fraction of shares
            print(self.state[1])
            begin_total_asset = self.state[0] + sum(
                np.array(self.state[1 : (self.data_feed.num_tickers + 1)])
                * np.array(
                    self.state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
            )

            argsort_actions = np.argsort(actions)

            sell_index = argsort_actions[: np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][: np.where(actions > 0)[0].shape[0]]

            for index in sell_index:
                # print(f"Num shares before: {self.state[index+self.data_feed.num_tickers+1]}")
                # print(f'take sell action before : {actions[index]}')
                actions[index] = self._sell(index, actions[index]) * (-1)
                # print(f'take sell action after : {actions[index]}')
                # print(f"Num shares after: {self.state[index+self.data_feed.num_tickers+1]}")

            for index in buy_index:
                # print('take buy action: {}'.format(actions[index]))
                actions[index] = self._buy(index, actions[index])

            self.actions_memory.append(actions)

            # state: s -> s+1
            self.time += 1
            self.df = self.data.loc[self.time, :]
            self.state = self._update_state()

            end_total_asset = self.state[0] + sum(
                np.array(self.state[1 : (self.data_feed.num_tickers + 1)])
                * np.array(
                    self.state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
            )
            self.asset_memory.append(end_total_asset)
            self.date_memory.append(self._get_date())
            self.reward = end_total_asset - begin_total_asset
            self.rewards_memory.append(self.reward)
            self.reward = self.reward * self.reward_scaling

        return self.state, self.reward, self.terminal, {}

    def _convert_action(self, action):
        """Used if actions need to be transformed without having to change entire step() method"""
        return action

    def _initiate_state(self):
        if self.initial:
            # For Initial State
            if len(self.data_feed.data.ticker.unique()) > 1:
                # for multiple stock
                state = (
                    [self.initial_balance]
                    + self.data.close.values.tolist()
                    + [0] * self.data_feed.num_tickers
                )
            else:
                # for single stock
                state = (
                    [self.initial_balance]
                    + [self.data.close]
                    + [0] * self.data_feed.num_tickers
                )
        else:
            # Using Previous State
            if len(self.data_feed.data.ticker.unique()) > 1:
                # for multiple stock
                state = (
                    [self.previous_state[0]]
                    + self.data.close.values.tolist()
                    + self.previous_state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
            else:
                # for single stock
                state = (
                    [self.previous_state[0]]
                    + [self.data.close]
                    + self.previous_state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
        return state

    def _update_state(self):
        if len(self.data.ticker.unique()) > 1:
            # for multiple stock
            state = (
                [self.state[0]]
                + self.data.close.values.tolist()
                + list(
                    self.state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
            )

        else:
            # for single stock
            state = (
                [self.state[0]]
                + [self.data.close]
                + list(
                    self.state[
                        (self.data_feed.num_tickers + 1) : (
                            self.data_feed.num_tickers * 2 + 1
                        )
                    ]
                )
            )

        return state

    def _get_date(self):
        if len(self.data.ticker.unique()) > 1:
            date = self.data.date.unique()[0]
        else:
            date = self.data.date
        return date

    def save_asset_memory(self):
        date_list = self.date_memory
        asset_list = self.asset_memory
        # print(len(date_list))
        # print(len(asset_list))
        df_account_value = pd.DataFrame(
            {"date": date_list, "account_value": asset_list}
        )
        return df_account_value

    def save_action_memory(self):
        if len(self.data.ticker.unique()) > 1:
            # date and close price length must match actions length
            date_list = self.date_memory[:-1]
            df_date = pd.DataFrame(date_list)
            df_date.columns = ["date"]

            action_list = self.actions_memory
            df_actions = pd.DataFrame(action_list)
            df_actions.columns = self.data.tic.values
            df_actions.index = df_date.date
            # df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        else:
            date_list = self.date_memory[:-1]
            action_list = self.actions_memory
            df_actions = pd.DataFrame({"date": date_list, "actions": action_list})
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def build_observation_space(self):
        pass

    def build_observation(self):
        pass

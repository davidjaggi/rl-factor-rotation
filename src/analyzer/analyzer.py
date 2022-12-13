from abc import ABC

import matplotlib.pyplot as plt
import pandas as pd


class Analyzer(ABC):
    def __init__(self, env):
        self.env = env
        self.broker = env.broker
        self.data = self._consolidation(env.broker.hist_dict)

    def _consolidation(self, hist_dict):

        index_list = [k for k in hist_dict.keys() if k != "historical_asset_prices"]
        multiindex = pd.MultiIndex.from_product(
            [index_list, ['timestamp', 'cash', 'positions', 'portfolio_values', 'portfolio_weights', 'ideal_weights']])
        # df from multiindex
        df = pd.DataFrame(index=hist_dict["benchmark"]['timestamp'], columns=multiindex)
        # iterate over multiindex
        for key in ["benchmark", "rl"]:
            df[key, 'timestamp'] = hist_dict[key]['timestamp']
            df[key, 'cash'] = hist_dict[key]['cash']
            df[key, 'positions'] = hist_dict[key]['positions']
            df[key, 'portfolio_values'] = hist_dict[key]['portfolio_values']
            df[key, 'portfolio_weights'] = hist_dict[key]['portfolio_weights']
            df[key, 'ideal_weights'] = hist_dict[key]['ideal_weights']
        # iterate through multiindex
        for key in ["benchmark", "rl"]:
            for col in ["positions", "portfolio_values", "portfolio_weights", "ideal_weights"]:
                if col == "positions":
                    prefix = "position_"
                elif col == "portfolio_values":
                    prefix = "value_"
                elif col == "portfolio_weights":
                    prefix = "weight_"
                elif col == "ideal_weights":
                    prefix = "ideal_weight_"
                # explode the list of dicts into new multiindex columns
                df_intermediate = pd.json_normalize(df[key, col])
                # rename the columns
                for colname in df_intermediate.columns:
                    df[key, prefix + colname] = df_intermediate[colname].values
                # df[key, col] = df[]

        # get all keys from list of dict
        df_prices = pd.DataFrame.from_dict(hist_dict['historical_asset_prices'])
        prices_intermediate = pd.json_normalize(df_prices['prices'])
        prices_intermediate["timestamp"] = df_prices["timestamp"]

        for colname in prices_intermediate.columns:
            df["historical_asset_prices", colname] = prices_intermediate[colname].values

        return df

    def get_positions(self, portfolio):
        df = self.data[portfolio]
        cols = df.columns.str.contains(r"position_")
        df = df.loc[:, cols]
        return df

    def get_weights(self, portfolio):
        df = self.data[portfolio]
        mask1 = df.columns.str.contains(r"weight_")
        mask2 = ~df.columns.str.contains(r"weight_total_value")
        mask3 = ~df.columns.str.contains(r"ideal_weight_")
        cols = mask1 & mask2 & mask3
        df = df.loc[:, cols]
        return df

    def get_ideal_weights(self, portfolio):
        df = self.data[portfolio]
        mask1 = df.columns.str.contains(r"ideal_weight_")
        #mask2 = ~df.columns.str.contains(r"weight_total_value")
        #mask3 = ~df.columns.str.contains(r"ideal_weight_")
        #cols = mask1 & mask2 & mask3
        cols = mask1
        df = df.loc[:, cols]
        return df

    def get_values(self, portfolio):
        df = self.data[portfolio]
        cols = df.columns.str.contains(r"value_")
        df = df.loc[:, cols]
        return df

    def get_cash(self, portfolio):
        df = self.data[portfolio]
        cols = df.columns.str.contains(r"cash")
        df = df.loc[:, cols]
        return df

    def get_prices(self):
        df = self.data["historical_asset_prices"]
        # drop timestamp
        df = df.drop(columns=["timestamp"])
        return df

    def get_timestamp(self, portfolio):
        df = self.data[portfolio]
        cols = df.columns.str.contains(r"timestamp")
        df = df.loc[:, cols]
        return df

    def get_rewards(self):
        return self.env.rewards_memory

    def get_actions(self):
        return self.env.actions_memory

    def plot_reward(self):
        df = self.get_rewards()
        plt.plot(df)
        plt.xlabel("Step")
        plt.ylabel("Reward")
        plt.title("Reward over time")
        plt.show()

    def compare(self):
        df = self.data.copy()

        bm_assets = self.env.config["benchmark_portfolio"]["investment_universe"]
        rl_assets = self.env.config["rl_portfolio"]["investment_universe"]

        for port in ["benchmark", "rl"]:
            df[port, "calc_total_value"] = df[port, "value_cash"]
            for asset in bm_assets:
                # sum up all positions
                df[port, "calc_total_value"] = df[port, "calc_total_value"] + (
                            df[port, f"position_{asset}"] * df["historical_asset_prices", asset])
            for asset in bm_assets:
                df[port, f"calc_weight_{asset}"] = (df[port, f"position_{asset}"] * df[
                    "historical_asset_prices", asset]) / df[port, f"calc_total_value"]
                df[port, f"diff_weight_{asset}"] = df[port, f"calc_weight_{asset}"] - df[port, f"calc_weight_{asset}"]
            df[port, "diff_total_value"] = df[port, "calc_total_value"] - df[port, "value_total_value"]
        return df

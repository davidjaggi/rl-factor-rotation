from abc import ABC

import pandas as pd
import numpy as np


class Backtester(ABC):

    def __init__(self, wealth, t_cost):

        self.wealth = wealth
        self.t_cost = t_cost
        self.reset()

    def reset(self):
        self.perf = []
        self.weights = []
        self.dates = []
        self.rebalance_dates = []

    def backtest_step(self, wgts, data_feed, wgts_dt=None, to_date=None):

        if isinstance(wgts, pd.DataFrame):
            if wgts_dt is None:
                wgts_dt = wgts.index.tolist()
            wgts = wgts.values

        if wgts.shape[0] != len(wgts_dt):
            raise ValueError("Weights and dates must have same lenght")

        if set(self.rebalance_dates).intersection(set(set(wgts_dt))):
            raise ValueError("Values have already been computed, call reset before running backtest again!")

        if to_date is None:
            to_date = wgts_dt[-1]

        if len(self.perf) == 0:
            # initialize class variables with more info from the data feed...
            self.perf_at_prev_reb = self.wealth
            self.perf_before_costs_at_reb = self.wealth
            self.units = np.zeros((1, data_feed.num_assets))
            self.sigs = np.zeros((1, data_feed.num_assets))
            self.cum_rets = np.zeros((1, data_feed.num_assets))
            self.cum_costs = np.zeros((1, data_feed.num_assets))
            start_date = wgts_dt[0]
            start_idx = 0
        else:
            start_date = self.dates[-1]
            start_idx = 1
        data = data_feed.get_price_data(end_dt=to_date, start_dt=start_date)

        wgt_idx = 0
        for i in range(start_idx, len(data)):

            if i > 0:
                added = self.units[-1, :] * self.sigs[-1, :] * (data.iloc[i, :].values - data.iloc[i - 1, :].values)
                if data.index[i - 1] in self.rebalance_dates:
                    # FX conversion can easily be incorporated into the cumrets
                    self.cum_rets = added
                    # only needs to be here if different costs are factored in
                    self.cum_costs = np.zeros((1, data_feed.num_assets))
                else:
                    self.cum_rets = self.cum_rets + added

            self.perf_before_costs_at_reb = self.perf_at_prev_reb + np.sum(self.cum_rets)

            if data.index[i] in wgts_dt:
                self.rebalance_dates.append(data.index[i])
                units = np.abs(wgts[wgt_idx, :]) * self.perf_before_costs_at_reb / data.iloc[i, :].values
                sigs = np.sign(wgts[wgt_idx, :])
                self.cum_costs = self.cum_costs + self.t_cost * np.abs(units * sigs * data.iloc[i, :].values -
                                                                       self.units[-1, :] * self.sigs[-1, :] * data.iloc[
                                                                                                              i - 1,
                                                                                                              :].values)
                self.units = np.append(self.units, units.reshape((1, units.shape[0])), axis=0)
                self.sigs = np.append(self.sigs, sigs.reshape((1, sigs.shape[0])), axis=0)
                wgt_idx += 1

            self.perf.append(self.perf_at_prev_reb + np.sum(self.cum_rets) - np.sum(self.cum_costs))
            self.dates.append(data.index[i])

            if data.index[i] in wgts_dt:
                self.perf_at_prev_reb = self.perf[-1]

        return self.dates, self.perf

    @property
    def performance(self):
        return pd.DataFrame({"Date": self.dates,
                             "Performance": self.perf}).set_index("Date")


if __name__ == "__main__":

    from src.data.feed import CSVDataFeed

    # define data feed
    feed = CSVDataFeed(file_name="example_data.csv")

    # instantiate backtester with st
    bt = Backtester(1000, 0.001)

    # get rebalancing frequencies and weights (i.e.: actions)
    dts = [pd.to_datetime("2019-12-31"), pd.to_datetime("2020-06-30")]
    wgts = np.array([[0.5, 0.5], [0.5, 0.5]])

    # backtest this
    _, _ = bt.backtest_step(wgts, feed, dts)
    perf = bt.performance
    perf.plot()

    # reset the backtester and do this in steps
    bt.reset()
    _, _ = bt.backtest_step(wgts[0, :].reshape((1,2)), feed, [dts[0]])
    _, _ = bt.backtest_step(wgts[1, :].reshape((1,2)), feed, [dts[1]])
    perf1 = bt.performance
    print(pd.concat([perf1, perf], axis=1).head())

    # simulate until time before next rebalancing and pick up again
    bt.reset()
    _, _ = bt.backtest_step(wgts[0, :].reshape((1, 2)), feed, [dts[0]], to_date=pd.to_datetime("2020-06-24"))
    perf_check = pd.concat([perf.iloc[:-1, :], perf1.iloc[:-1, :], bt.performance], axis=1)
    _, _ = bt.backtest_step(wgts[1, :].reshape((1, 2)), feed, [dts[1]])
    print(pd.concat([perf, perf1, bt.performance], axis=1).tail())

    # test the same with a dataframe
    df = pd.DataFrame(wgts)
    df["Date"] = dts
    df = df.set_index("Date")
    bt.reset()
    _, _ = bt.backtest_step(df, feed)
    perf_df = bt.performance

    # test this on fake data...
    class FakeFeed:
        asset1 = [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61]
        asset2 = [50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39]
        df = pd.DataFrame({"Asset1": asset1, "Asset2": asset2})
        num_assets = 2

        def get_price_data(self, end_dt, start_dt, offset=None):
            return self.df

    f = FakeFeed()
    bt_fake = Backtester(1000, 0.001)

    # get rebalancing frequencies and weights (i.e.: actions)
    dts = [0, 4, 8]
    wgts = np.array([[0.5, -0.5], [0.5, -0.5], [0.5, -0.5]])
    _, _ = bt_fake.backtest_step(wgts, f, dts)
    # end perf without TA-costs is: 1238.813450
    # end perf with TA-costs of 0.001 is: 1237.490527
    print(bt_fake.tail())
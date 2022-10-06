import copy
import numpy as np
from abc import ABC
from datetime import datetime
from decimal import Decimal


class Broker(ABC):
    """ Broker class
    Args:
    """

    def __init__(self, data_feed,):

        self.data_feed = data_feed
        self.benchmark_portfolio = None
        self.rl_portfolio = None
        self.hist_dict = {'benchmark': {'timestamp': [], 'holdings': []},
                          'rl': {'timestamp': [], 'holdings': []},
                          'historical_asset_prices': []}
        self.trade_logs = {'benchmark_portfolio': [],
                           'rl_portfolio': []}

    def reset(self, portfolio):
        """ Resetting the Broker class

        """

        self.data_feed.reset(time=portfolio.start_time)
        dt, lob = self.data_feed.next_prices_snapshot()

        # reset the Broker logs
        if type(portfolio).__name__ != 'RL_portfolio':
            self.hist_dict['benchmark']['timestamp'] = []
            self.hist_dict['benchmark']['holdings'] = []
            self.trade_logs['benchmark_portfolio']= []
            self.current_dt_bmk = dt
        else:
            self.hist_dict['rl']['timestamp'] = []
            self.hist_dict['rl']['lob'] = []
            self.trade_logs['rl_portfolio'] = []
            self.current_dt_rl = dt

        # update to the first instance of the datafeed & record this
        portfolio.reset()
        self._record_prices(dt, lob, portfolio)

    def _record_prices(self, dt, prices, portfolio):
        #TODO: Start here tomorrow



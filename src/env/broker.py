from abc import ABC


class Broker(ABC):
    """ Broker class
    Args:
    """

    def __init__(self, data_feed, config):
        self.data_feed = data_feed
        self.config = config
        self.benchmark_portfolio = self.config['benchmark_portfolio']
        self.rl_portfolio = self.config['rl_portfolio']
        self.hist_dict = self._create_hist_dict()
        self.trade_logs = self._create_trade_log()

    def _create_hist_dict(self):
        return {'benchmark':
                    {'timestamp': [], 'holdings': [], 'cash': []},
                'rl': {'timestamp': [], 'holdings': []},
                'historical_asset_prices': []}

    def _create_trade_log(self):
        return {'benchmark_portfolio': [],
                'rl_portfolio': []}

    def reset(self, portfolio):
        """ Resetting the Broker class """
        self.data_feed.reset(time=portfolio.start_time)
        dt, lob = self.data_feed.next_prices_snapshot()

        # reset the Broker logs
        if type(portfolio).__name__ != 'rl_portfolio':
            self.hist_dict['benchmark']['timestamp'] = []
            self.hist_dict['benchmark']['holdings'] = []
            self.trade_logs['benchmark_portfolio'] = []
            self.current_dt_bmk = dt

        else:
            self.hist_dict['rl']['timestamp'] = []
            self.hist_dict['rl']['lob'] = []
            self.trade_logs['rl_portfolio'] = []
            self.current_dt_rl = dt

        # update to the first instance of the datafeed & record this
        portfolio.reset()
        self._record_prices(dt, lob, portfolio)

    def _record_prices(self, portfolio, prices):
        """ Record the prices of the assets in the portfolio and append it to the hist dict """
        # TODO: Check how we store/manipulate prices
        if portfolio.dt != prices.dt:
            raise ValueError(" Mismatch between timestamps of prices and portfolio.")

        self.hist_dict['historical_asset_prices'].append(({'timestamp': portfolio.dt,
                                                           'prices': prices, }))

    def _record_position(self, portfolio):
        """ Record the position of the portfolio and append it to the hist dict for the correct portfolio """
        if type(portfolio).__name__ != 'RL_portfolio':

            self.hist_dict['benchmark']['timestamp'].append(portfolio.dt)
            self.hist_dict['benchmark']['holdings'].append(portfolio.holdings)

        else:

            self.hist_dict['rl']['timestamp'].append(portfolio.dt)
            self.hist_dict['rl']['holdings'].append(portfolio.holdings)

    def rebalance(self, date):

        if benchmark_portfolio.rebalancing_schedule(date):

            self.shares_to_trade = get_trades_for_rebalance()
            self.cash_delta = self.shares_to_trade[0]*self.hist_dict['historical_asset_prices'][-1][0]+\
                              self.shares_to_trade[1]*self.hist_dict['historical_asset_prices'][-1][1]

            if len(self.hist_dict['benchmark']['cash'][-1]) != 0:
                self.hist_dict['benchmark']['cash'].append(self.hist_dict['benchmark']['cash'][-1]*self.cash_delta-
                                                           trx_cost*(abs(shares_to_trade[0])+abs(shares_to_trade[0])))
            else:
                self.hist_dict['benchmark']['cash'].append(10000 * self.cash_delta-
                                                           trx_cost*(abs(shares_to_trade[0])+abs(shares_to_trade[0])))

            self.hist_dict['benchmark']['timestamp'].append(date)
            self.new_holdings = [self.hist_dict['benchmark']['holdings'][-1][0]+shares_to_trade[0],
                                 self.hist_dict['benchmark']['holdings'][-1][1]+shares_to_trade[1]]
            self.hist_dict['benchmark']['holdings'].append(self.new_holdings)

        else:
            pass
            #("Not the last bday of the month, no rebalancing!!")


    def get_trades_for_rebalance(self):
    #TODO: This function should look at a potrfolio's ideal weights and holdings and output
    # the necessary trades to rebalance the holdings accordingly
        ratio = round(self.hist_dict['historical_asset_prices'][-1][0] / (self.hist_dict['historical_asset_prices'][-1][0] +
                                                                     self.hist_dict['historical_asset_prices'][-1][1]), 2)

        curr_weight = [ratio, 1 - ratio]
        ideal_weights = [0.5, 0.5]
        delta = list()

        for a, b in zip(curr_weight, ideal_weights):
            delta.append(round(a - b, 2))

        self.shares_to_trade = [round(delta[0] * self.hist_dict['benchmark']['holdings'][-1][0],0),
                           round(delta[1] * self.hist_dict['benchmark']['holdings'][-1][1],0)]

        #TODO: implement the ENV_CONFIG = initial_balance within this function to check if we have enough money to trade (cash within hist_dict)

        return shares_to_trade






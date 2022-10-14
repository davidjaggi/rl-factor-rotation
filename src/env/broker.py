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
        self.transaction_cost = self.config['transaction_cost']
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
            self.portfolio_value = {'GOOGLE': 1, 'APPLE': 1}
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

        if self.benchmark_portfolio.rebalancing_schedule(date):

            self.shares_to_trade = self.get_trades_for_rebalance()

            self.cash_google = self.shares_to_trade[0] * self.hist_dict['historical_asset_prices']['GOOGLE'][-1]
            self.cash_apple = self.shares_to_trade[1] * self.hist_dict['historical_asset_prices']['APPLE'][-1]

            if self.cash_google > 0:
                if self.cash_apple * -1 + self.hist_dict['benchmark']['cash'][-1] > self.cash_google:
                    pass
                else:
                    self.nr_shares_g = self.nr_shares_g - (self.cash_google + self.cash_apple - self.hist_dict['benchmark']['cash'][-1]) / \
                                  self.hist_dict['historical_asset_prices']['GOOGLE'][-1]
                    self.shares_to_trade = [round(self.nr_shares_g, 0), round(self.nr_shares_a, 0)]
                    self.cash_google = self.shares_to_trade[0] * self.hist_dict['historical_asset_prices']['GOOGLE'][-1]

            else:
                if self.cash_google * -1 + self.hist_dict['benchmark']['cash'][-1] > self.cash_apple:
                    pass
                else:
                    self.nr_shares_a = self.nr_shares_a - (self.cash_apple + self.cash_google - self.hist_dict['benchmark']['cash'][-1]) / \
                                  self.hist_dict['historical_asset_prices']['APPLE'][-1]
                    self.shares_to_trade = [round(self.nr_shares_g, 0), round(self.nr_shares_a, 0)]
                    self.cash_apple = self.shares_to_trade[1] * self.hist_dict['historical_asset_prices']['APPLE'][-1]

            self.cash_delta = self.cash_google + self.cash_apple

            self.hist_dict['benchmark']['cash'].append(self.hist_dict['benchmark']['cash'][-1] - self.cash_delta -
                                                  self.trx_cost * (abs(self.shares_to_trade[0]) + abs(self.shares_to_trade[1])))

            self.hist_dict['benchmark']['timestamp'].append(date)

            self.new_holdings_g = self.hist_dict['benchmark']['holdings']['GOOGLE'][-1] + self.shares_to_trade[0]
            self.new_holdings_a = self.hist_dict['benchmark']['holdings']['APPLE'][-1] + self.shares_to_trade[1]

            self.hist_dict['benchmark']['holdings']['GOOGLE'].append(self.new_holdings_g)
            self.hist_dict['benchmark']['holdings']['APPLE'].append(self.new_holdings_a)


        else:
            pass
            #("Not the last bday of the month, no rebalancing!!")


    def get_trades_for_rebalance(self):
    #TODO: This function should look at a potrfolio's ideal weights and holdings and output
    # the necessary trades to rebalance the holdings accordingly

        self.portfolio_value = self.get_portfolio_value() #

        self.ratio = (self.portfolio_value['GOOGLE']) / (self.portfolio_value['GOOGLE'] + self.portfolio_value['APPLE'])

        self.curr_weight = [ratio, 1 - ratio]
        self.ideal_weights = [0.5, 0.5]
        self.delta = list()

        for a, b in zip(self.curr_weight, self.ideal_weights):
            self.delta.append((a * -1) - (b * -1))

        self.delta_portfolio_value = self.portfolio_value['GOOGLE'] - self.portfolio_value['APPLE']

        if self.delta_portfolio_value > 0:
            self.nr_shares_g = self.delta_portfolio_value / 2 / self.hist_dict['historical_asset_prices']['GOOGLE'][-1] * -1
            self.nr_shares_a = self.delta_portfolio_value / 2 / self.hist_dict['historical_asset_prices']['APPLE'][-1]
        else: ## NOT SURE IF NEEDED, MAYBE FOR EDGE CASES
            self.nr_shares_g = self.delta_portfolio_value / 2 / self.hist_dict['historical_asset_prices']['GOOGLE'][-1] * -1 ## NOT SURE IF NEEDED, MAYBE FOR EDGE CASES
            self.nr_shares_a = self.delta_portfolio_value / 2 / self.hist_dict['historical_asset_prices']['APPLE'][-1] ## NOT SURE IF NEEDED, MAYBE FOR EDGE CASES

        self.shares_to_trade = [round(self.nr_shares_g, 0), round(self.nr_shares_a, 0)]

        return self.shares_to_trade


    def get_portfolio_value(self):

        self.portfolio_value['GOOGLE'] = self.hist_dict['benchmark']['holdings']['GOOGLE'][-1] * \
                                    self.hist_dict['historical_asset_prices']['GOOGLE'][-1]
        self.portfolio_value['APPLE'] = self.hist_dict['benchmark']['holdings']['APPLE'][-1] * \
                                   self.hist_dict['historical_asset_prices']['APPLE'][-1]

        return self.portfolio_value


from abc import ABC

from src.env.portfolio import Portfolio


class Broker(ABC):
    """ Broker class
    Args:
    """

    def __init__(self, data_feed, config):
        self.data_feed = data_feed
        self.config = config # TODO: This makes it so that we store the portfolios twice, once in the config and again in the Broker, I suggest we delete it.
        self.transaction_cost = self.config['transaction_cost']
        self.start_date = self.config['start_date']
        self.hist_dict = self._create_hist_dict()
        self.trade_logs = self._create_trade_logs()

    def _create_hist_dict(self):
        return {'benchmark': {'timestamp': [], 'positions': [], 'cash': []},
                'rl': {'timestamp': [], 'positions': [], 'cash': []}, 'historical_asset_prices': []}

    def _create_trade_logs(self):
        return {'benchmark': [],
                'rl': []}

    def reset(self, portfolio, idx: int):
        """ Resetting the Broker class """
        self.data_feed.reset(start_dt=self.start_date, end_dt=None)
        prices = self.data_feed.get_prices_snapshot(idx)
        date = self.data_feed.get_date(idx)

        # reset the Broker logs
        if type(portfolio).__name__ != 'RLPortfolio':
            self.hist_dict['benchmark']['portfolio_values'] = []
            self.hist_dict['benchmark']['portfolio_weights'] = []
            self.hist_dict['benchmark']['timestamp'] = []
            self.hist_dict['benchmark']['positions'] = []
            self.trade_logs['benchmark'] = []

        else:
            self.hist_dict['rl']['portfolio_values'] = []
            self.hist_dict['rl']['portfolio_weights'] = []
            self.hist_dict['rl']['timestamp'] = []
            self.hist_dict['rl']['positions'] = []
            self.trade_logs['rl'] = []

        # reset the historical asset prices
        self.hist_dict['historical_asset_prices'] = []
        # update to the first instance of the datafeed & record this
        portfolio.reset(self.start_date, prices)
        self._record_prices(prices, date)
        # record the initial positions of the portfolio
        self._record_positions(portfolio, date)

        return portfolio


    def update_ideal_weights(self, portfolio, delta):
        for key, value in portfolio.ideal_weights.items():
            portfolio.ideal_weights[key] = value + delta[key]


    def _record_prices(self, prices, date):
        """ Record the prices of the assets in the portfolio and append it to the hist dict """
        # filter prices to only contain Price Open
        prices = {k: v['Price Open'] for k, v in prices.items()}

        if len(self.hist_dict['historical_asset_prices'])==0:
            self.hist_dict['historical_asset_prices'].append(({'timestamp': date, 'prices': prices}))
        elif date != self.hist_dict['historical_asset_prices'][-1]['timestamp']:
            self.hist_dict['historical_asset_prices'].append(({'timestamp': date, 'prices': prices}))
        else:
            pass


    def _record_positions(self, portfolio, date):
        """ Record the positions of the portfolio (and avalilable cash) and append it to the hist dict for the correct portfolio """
        if type(portfolio).__name__ != 'RLPortfolio':

            self.hist_dict['benchmark']['timestamp'].append(date)
            self.hist_dict['benchmark']['positions'].append(portfolio.positions)
            self.hist_dict['benchmark']['cash'].append(portfolio.cash_position)
            self.hist_dict['benchmark']['weight'].append(portfolio.portfolio_weights)
            self.hist_dict['benchmark']['values'].append(portfolio.portfolio_values)

        else:

            self.hist_dict['rl']['timestamp'].append(date)
            self.hist_dict['rl']['positions'].append(portfolio.positions)
            self.hist_dict['rl']['cash'].append(portfolio.cash_position)
            self.hist_dict['rl']['weight'].append(portfolio.portfolio_weights)
            self.hist_dict['rl']['values'].append(portfolio.portfolio_values)

    def rebalance(self, date, prices, portfolio):  # TODO: rename function to rebalance_and_log
        # TODO: If we decide to have multiple benchmark portfolios, we can put them in a list and turn this function into a loop
        self.rebalance_portfolio(date, prices, portfolio)
        # record the prices for the specific period
        self._record_prices(prices, date)

    def rebalance_portfolio(self, date, prices, portfolio: Portfolio):
        # In the first step we want to take the ideal weights of the portfolio and adjust them

        # check if the current date is equal to a rebalance date
        if portfolio.rebalancing_schedule.check_rebalance_date(date):

            rebalance_dict = self.get_trades_for_rebalance(portfolio, prices)

            # Now we need to see whether we can carry out the proposed transactions given the portfolio's positions & cash balance (remember the transaction shares are rounded)

            # First we check if we have enough shares to sell

            for i, (asset, transaction) in enumerate(rebalance_dict.items()):
                if rebalance_dict[asset]['transaction_shares'] < 0:
                    # We need to check that we have actually enough shares to sell in each sell transaction
                    if portfolio.positions[asset] < -rebalance_dict[asset]['transaction_shares']:
                        # If we don't have enough shares we scale down the sale
                        rebalance_dict[asset]['transaction_shares'] = -portfolio.positions[asset]

            incoming_cash = 0
            outgoing_cash = 0

            for i, (asset, transaction_dict) in enumerate(rebalance_dict.items()):
                if transaction_dict['transaction_shares'] < 0:
                    incoming_cash += -transaction_dict['transaction_value'] #TODO: Transaction costs should be accounted for in this line(s)
                else:
                    outgoing_cash += transaction_dict['transaction_value']

            while incoming_cash + portfolio.cash_position < outgoing_cash:
                # We don't have enough capital to carry out the rebalance, we scale down the trades until we do.
                for i, (asset, transaction) in enumerate(rebalance_dict.items()):
                    if incoming_cash + portfolio.cash_position < outgoing_cash and transaction['transaction_shares'] > 0:
                        # We need to scale down this purchase
                        available_capital = incoming_cash + portfolio.cash_position
                        rebalance_dict[asset]['transaction_shares'] += -int((outgoing_cash - (available_capital))/prices[asset]) - 1 #
                        # Update the outgoing cash
                        outgoing_cash += (-int((outgoing_cash - (available_capital))/prices[asset]) - 1)*prices[asset]
                        #TODO: Currently this only scales down the first "buy" transaction it finds in the dictionary, if we are buying more than one asset we would have to implement a "scale down method" (for example buy 1 share less iteratively from all buys until we have enough capital)
            # We now have enough capital to carry out the rebalance so we carry out the trades and update our cash and positions
            for i, (asset, transaction) in enumerate(rebalance_dict.items()):
                portfolio.positions[asset] += rebalance_dict[asset]['transaction_shares']
            # We record the change in cash
            portfolio.cash_position += incoming_cash - outgoing_cash

            # TODO: If the cash position left is bigger than the price of some of the buys, we scale up the buys of the portfolio
            prices_buys = [price for i, (asset, price) in enumerate(prices.items()) if
                           rebalance_dict[asset]['transaction_shares'] > 0]
            while portfolio.cash_position > min(prices_buys):
                for i, (asset, transaction) in enumerate(rebalance_dict.items()):
                    if portfolio.cash_position > prices[asset] and rebalance_dict[asset]['transaction_shares'] > 0:
                        # We buy one more share of said asset
                        portfolio.positions[asset] += 1
                        portfolio.cash_position += -prices[asset]

            # Record the trades in the trade logs
        self._record_positions(portfolio, date)

    def get_trades_for_rebalance(self, portfolio: Portfolio, prices):
        """" Get the necessary transactions to carry out a Portfolio's rebalance given its current positions,
        ideal_weights and rebalancing_type.
        """
        # TODO: If instead of copying the ideal_weights we want to use them as a signal to trade, that should be implemented here. Right now the difference between weights determines the transaction.

        portfolio_values, portfolio_weights = self.get_portfolio_value_and_weights(portfolio, prices)

        # Now that we have the portfolio weights we calculate the delta (difference) between the ideal weight of
        # each position and its current weight
        rebalance_dict = {}

        for i, (asset, weight) in enumerate(portfolio_weights.items()):
            transaction_currency_value = (portfolio.ideal_weights[asset] - portfolio_weights[asset] )*portfolio_values['total_value']
            rebalance_dict[asset] = {'transaction_shares': int(transaction_currency_value/prices[asset])}
            rebalance_dict[asset]['transaction_value'] = rebalance_dict[asset]['transaction_shares']*prices[asset]

        return rebalance_dict


    def get_portfolio_value_and_weights(self, portfolio, prices):
        portfolio_values = {}
        portfolio_weights = {}
        for i, (asset, position) in enumerate(portfolio.positions.items()):
            portfolio_values[asset] = position * prices[asset]

        portfolio_values['total_value'] = sum(portfolio.values())

        for i, (asset, position_value) in enumerate(portfolio_values):
            portfolio_weights[asset] = portfolio_values[asset]/portfolio_values['total_value']

        return portfolio_values, portfolio_weights

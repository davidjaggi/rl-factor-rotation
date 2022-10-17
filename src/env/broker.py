from abc import ABC
from src.env.portfolio import Portfolio

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
        self.trade_logs = self._create_trade_logs()


    def _create_hist_dict(self):
        return {'benchmark_portfolio':{'timestamp': [], 'holdings': [], 'cash': []},
                       'rl_portfolio':{'timestamp': [], 'holdings': [], 'cash': []}, 'historical_asset_prices': []}


    def _create_trade_logs(self):
        return {'benchmark_portfolio': [],
                'rl_portfolio': []}


    def reset(self, portfolio : Portfolio):
        """ Resetting the Broker class """
        self.data_feed.reset(time=portfolio.start_date)
        dt, prices = self.data_feed.next_prices_snapshot()

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
        portfolio.reset(portfolio.start_date, prices)
        self._record_prices(portfolio, prices)


    def _record_prices(self, portfolio, prices):
        """ Record the prices of the assets in the portfolio and append it to the hist dict """
        # TODO: Check how we store/manipulate prices
        if portfolio.dt != prices.dt:
            raise ValueError(" Mismatch between timestamps of prices and portfolio.")

        self.hist_dict['historical_asset_prices'].append(({'timestamp': portfolio.dt,
                                                           'prices': prices, }))


    def _record_positions(self, portfolio):
        """ Record the positions of the portfolio (and avalilable cash) and append it to the hist dict for the correct portfolio """
        if type(portfolio).__name__ != 'RLPortfolio':

            self.hist_dict['benchmark']['timestamp'].append(portfolio.dt)
            self.hist_dict['benchmark']['holdings'].append(portfolio.holdings)
            self.hist_dict['benchmark']['cash'] = portfolio.cash_position

        else:

            self.hist_dict['rl']['timestamp'].append(portfolio.dt)
            self.hist_dict['rl']['holdings'].append(portfolio.holdings)
            self.hist_dict['rl']['cash'] = portfolio.cash_position

    def rebalance(self, date, prices):
        # We first rebalance the benchmark portfolio
        if self.benchmark_portfolio.rebalancing_schedule(date):

            rebalance_dict = self.get_trades_for_rebalance(self.benchmark_portfolio, prices)

            # Now we need to see whether we can carry out the proposed transactions given our cash balance (remember the transaction shares are rounded)

            incoming_cash = 0
            outgoing_cash = 0

            for asset, transaction in enumerate(rebalance_dict):
                if transaction['transaction_shares'] < 0:
                    incoming_cash += -transaction['transaction_shares']*prices[asset] #TODO: Transaction costs should be accounted for in this line(s)
                else:
                    outgoing_cash += transaction['transaction_shares']*prices[asset]

            if incoming_cash + self.benchmark_portfolio.cash_position > outgoing_cash:
                # We have enough capital to carry out the rebalance, we carry out the trades and update our cash and positions
                for asset, transaction in enumerate(rebalance_dict):
                    self.benchmark_portfolio.positions[asset] += rebalance_dict[asset]['transaction_shares']

                self.benchmark_portfolio.cash_position += incoming_cash - outgoing_cash
            else:
                # We don't have enough capital to carry out the rebalance, we scale down the trades until we do.
                for asset, transaction in enumerate(rebalance_dict):
                    if transaction['transaction_shares'] > 0:
                        # We need to scale down this purchase
                        rebalance_dict[asset]['transaction_shares'] += -(outgoing_cash - (incoming_cash + self.benchmark_portfolio.cash_position))/prices[asset]
                        # Update the outgoing cash
                        outgoing_cash = rebalance_dict[asset]['transaction_shares']*prices[asset]
                #TODO: Currently this only works when ONLY 1 ASSET is sold, to generalize this we would have to implement a "scale down method".

                for asset, transaction in enumerate(rebalance_dict):
                    self.benchmark_portfolio.positions[asset] += rebalance_dict[asset]['transaction_shares']

                self.benchmark_portfolio.cash_position += incoming_cash - outgoing_cash

            #TODO: We need to decide what to do if the cash position left here is big, maybe increase the buying transactions? Otherwise it may start building up during the simulation

        if self.benchmark_portfolio.rebalancing_schedule(date):
            #TODO: Start here


    def get_trades_for_rebalance(self, portfolio: Portfolio, prices):
        """" Get the necessary transactions to carry out a Portfolio's rebalance given its current positions,
        ideal_weights and rebalancing_type.
        """
        #TODO: If instead of copying the ideal_weights we want to use them as a signal to trade, that should be implemented here. Right now the difference between weights determines the transaction.

        portfolio_values, portfolio_weights = self.get_portfolio_value_and_weights(portfolio, prices)

        # Now that we have the portfolio weights we calculate the delta (difference) between the ideal weight of
        # each position and its current weight
        rebalance_dict = {}

        for asset, weight in portfolio_weights:
            transaction_currency_value = (portfolio_weights[asset] - portfolio.ideal_weights[asset])*portfolio_values['total_value']
            rebalance_dict[asset] = {'transaction_value': transaction_currency_value,
                                 'transaction_shares': int(transaction_currency_value/prices[asset])}

        return rebalance_dict


    def get_portfolio_value_and_weights(self, portfolio, prices):
        portfolio_values = {}
        portfolio_weights = {}
        for asset, position in enumerate(portfolio.positions):
            portfolio_values[asset] = position * prices[asset]

        portfolio_values['total_value'] = sum(portfolio.values())

        for asset, position_value in enumerate(portfolio_values):
            portfolio_weights[asset] = round(portfolio_values[asset]/portfolio_values['total_value'],2)

        return portfolio_values, portfolio_weights


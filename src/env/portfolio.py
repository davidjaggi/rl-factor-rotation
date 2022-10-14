from abc import ABC

from pandas.tseries.offsets import BMonthEnd

offset = BMonthEnd()


def last_Bday_of_month(dt):
    return offset.rollforward(dt)


class Portfolio(ABC):
    """ Parent class for all portfolios.
    Args:
        initial_balance (dict): Initial holdings of the portfolio, in units of cash and assets.
        restrictions (list): list of boolean methods to apply to self.ideal_weights when rebalancing.
        start_date (Datetime): Starting date of the portfolio.
    """

    def __init__(self, config):
        # TODO: extract all variables of the config to the init method
        self.initial_balance = config["initial_balance"]
        self.balance = config["initial_balance"]
        self.initial_weights = config["initial_weights"]
        self.restrictions = config["restrictions"]
        self.start_date = config["start_date"]
        self.dt = config["start_date"]
        self.schedule = config["schedule"]
        self.type = config["type"]
        self.trade_idx = 0  # Trade Counter for testing

    def reset(self, start_date, prices):
        """"
        reset method of the Portfolio class.
        """
        self.balance = self.initial_balance
        self.positions = self._initial_rebalance(prices)
        self.dt = start_date
        self.trade_idx = 0

    def _check_rebalance(self, date):
        """ Check if the portfolio needs to be rebalanced.
        Args:
            date (Datetime): Current date of the portfolio.
        Returns:
            bool: True if the portfolio needs to be rebalanced, False otherwise.
        """
        if self.schedule == "monthly":
            return last_Bday_of_month(date) == date
        else:
            raise NotImplementedError

    def _initial_rebalance(self, prices):
        """Calculate the initial positions of the portfolio (without transaction costs for now)


        """
        positions = {}

        if self.type == "equally_weighted":
            number_of_assets = len(prices)
            for asset, price in enumerate(prices):
                positions[asset] = round((self.balance/number_of_assets)/price, 0)
                # Check if we have enough initial balance to initiate the position
                if positions[asset] > 0:
                    self.balance = self.balance - positions[asset]*price

        return positions



class BenchmarkPortfolio(Portfolio):

    def __init__(self, *args, **kwargs):
        super(BenchmarkPortfolio, self).__init__(*args, **kwargs)
        self.ideal_weights = [0.5, 0.5]

class RLPortfolio(Portfolio):

    def __init__(self, *args, **kwargs):
        super(RLPortfolio, self).__init__(*args, **kwargs)

        if self.type == "equally_weighted":
            self.ideal_weights = [0.5, 0.5]  # TODO move to 1/n

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
        self.balance = config["initial_balance"]
        self.initial_weights = config["initial_weights"]
        self.restrictions = config["restrictions"]
        self.start_date = config["start_date"]
        self.dt = config["start_date"]
        self.schedule = config["schedule"]
        self.type = config["type"]
        self.holdings = []
        self.trade_idx = 0  # Trade Counter for testing

    def reset(self):
        """"
        reset method of the Portfolio class.
        """
        #TODO: Do we need to reset more parameters?
        self.trade_idx = 0


class BenchmarkPortfolio(Portfolio):

    def __init__(self, *args, **kwargs):
        super(BenchmarkPortfolio, self).__init__(*args, **kwargs)
        self.ideal_weights = [0.5, 0.5]


class RLPortfolio(Portfolio):

    def __init__(self, *args, **kwargs):
        super(RLPortfolio, self).__init__(*args, **kwargs)

        if self.type == "equally_weighted":
            self.ideal_weights = [0.5, 0.5]


if __name__ == '__main__':
    schedule = rebalancing_schedule()
    portfolio_dict = {
        'name': 'benchmark_portfolio',
        'type': "equally_weighted",
        'initial_balance': 1000,
        'initial_weights': [0.5, 0.5],
        'restrictions': dict(),
        'start_date': '2020-02-24',
        'schedule': schedule
    }

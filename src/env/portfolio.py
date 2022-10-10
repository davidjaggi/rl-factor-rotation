import math
import copy
import numpy as np
from datetime import datetime, date
from pandas.tseries.offsets import BMonthEnd

offset = BMonthEnd()


from decimal import Decimal
from random import randint
import random
from abc import ABC


def last_Bday_of_month(dt):

    return offset.rollforward(dt)

class Portfolio(ABC):
    """ Parent class for all portfolios.
    Args:
        initial_holdings (dict): Initial holdings of the portfolio, in units of cash and assets.
        restrictions (list): list of boolean methods to apply to self.ideal_weights when rebalancing.
        start_date (Datetime): Starting date of the portfolio.
    """

    def __init__(self, initial_holdings, restrictions, start_date):
        #TODO: Do we need any other attributes?

        self.holdings = initial_holdings
        self.restrictions = restrictions
        self.start_date = start_date
        self.dt = start_date
        self.trade_idx = 0 # Trade Counter for testing

    def reset(self):
        """"
        reset method of the Portfolio class.
        """
        #TODO: Do we need to reset more parameters?
        self.trade_idx = 0


    def rebalancing_schedule(self, date):
        """
        Boolean Method that implements the rebalancing schedule, to be implemented by each individual portfolio.
        """
        raise NotImplementedError

class benchmark_portfolio(Portfolio):

    def __init__(self, *args, **kwargs):
        super(benchmark_portfolio, self).__init__(*args, **kwargs)
        self.ideal_weights = [0.5,0.5]

    def rebalancing_schedule(self, date):
        """
        The benchmark_portfolios update once a month on the last Business day.
        """
        return date == last_Bday_of_month(date)


class RL_portfolio(Portfolio):

    def __init__(self, *args, **kwargs):
        super(RL_portfolio, self).__init__(*args, **kwargs)
        self.ideal_weights = [0.5,0.5]

    def rebalancing_schedule(self, date):
        """
        The RL_portfolios update ...
        """
        # TODO: Change this if needed
        return date == last_Bday_of_month(date)

import pandas as pd
from pandas.tseries.offsets import BDay


class RebalancingSchedule:
    # see here for all possible alias schedules:
    # https://pandas.pydata.org/pandas-docs/version/0.24/user_guide/timeseries.html#timeseries-offset-aliases

    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date
        self.rebalancing_dates = []

    def set_start_and_end(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def remove_dates_from_schedule(self, remove_dates):
        self.rebalancing_dates = [x for x in self.rebalancing_dates if x not in remove_dates]
        return self.rebalancing_dates

    def add_dates_to_schedule(self, add_dates):
        pass

    def schedule(self):
        raise NotImplementedError


class PeriodicSchedule(RebalancingSchedule):
    def __init__(self, frequency, holidays=BDay, skip_day=None, skip_month=None, skip_year=None, *args, **kwargs):
        self.frequency = frequency
        self.holidays = holidays
        self.skip_day = skip_day
        self.skip_month = skip_month
        self.skip_year = skip_year
        super().__init__(*args, **kwargs)

    def schedule(self):
        if self.start_date is None or self.end_date is None:
            raise ValueError('Start and End Date have to be set!')

        # get all dates first
        pd_dates = pd.date_range(self.start_date, self.end_date, freq=self.frequency)

        # add another business day (IS THIS WORKING?)
        pd_dates = pd_dates.map(lambda x: x + 0*self.holidays())

        # skip whenever defined
        pd_dates = pd_dates.to_list()
        if self.skip_day is not None:
            pd_dates = [x for x in pd_dates if x.day not in self.skip_day]
        if self.skip_month is not None:
            pd_dates = [x for x in pd_dates if x.month not in self.skip_month]
        if self.skip_year is not None:
            pd_dates = [x for x in pd_dates if x.year not in self.skip_year]

        self.rebalancing_dates = pd_dates
        return pd_dates
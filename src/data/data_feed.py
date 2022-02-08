# %%
import pandas as pd
from pandas_datareader.data import DataReader
# %%
class DataFeed(object):
    # initialize datafeed
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.get_data()

    def get_data(self):
        # get data from public sources
        price_data = DataReader(self.tickers, 'stooq', self.start_date, self.end_date)['Close']
        all_weekdays = pd.date_range(start=self.start_date, end=self.end_date, freq='B')
        price_data = price_data.reindex(all_weekdays)
        price_data = price_data.fillna(method='ffill')
        price_data = self._preprocess(price_data)
        return price_data

    def _preprocess(self, price_data):
        # fill with all business days and include nan's where no data is available
        return price_data.stack().reset_index(name="close").rename(columns={"level_0":"date","Symbols":"ticker"})

# TODO here we can add custom datafeeds and other sources
# %%
data = DataFeed(tickers=['AAPL', 'MSFT', 'GOOG'], start_date='2017-01-01', end_date='2017-12-31')
data.data.head()
# %%

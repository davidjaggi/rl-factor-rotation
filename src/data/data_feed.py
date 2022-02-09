# %%
import pandas as pd
from pandas_datareader.data import DataReader

# %%
class BaseDataFeed(object):
    # initialize datafeed
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.num_tickers = len(tickers)
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.get_data()

    def get_data(self):
        # get data from public sources
        price_data = DataReader(self.tickers, "yahoo", self.start_date, self.end_date)
        # stack the dataframe

        all_weekdays = pd.date_range(start=self.start_date, end=self.end_date, freq="B")
        price_data = price_data.reindex(all_weekdays)
        price_data = price_data.fillna(method="ffill")
        price_data = self._preprocess(price_data)
        return price_data

    def _preprocess(self, price_data):
        # fill with all business days and include nan's where no data is available
        return (
            price_data.stack()
            .reset_index()
            .rename(
                columns={
                    "level_0": "date",
                    "Symbols": "ticker",
                    "Adj Close": "adj_close",
                    "Close": "close",
                    "High": "high",
                    "Low": "low",
                    "Open": "open",
                    "Volume": "volume",
                }
            )
        )


# %%
class StooqDataFeed(BaseDataFeed):
    # inherit from BaseDataFeed
    def __init__(self, tickers, start_date, end_date):
        super().__init__(tickers, start_date, end_date)

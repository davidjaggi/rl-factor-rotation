# %%
import pandas as pd
from pandas_datareader.data import DataReader


class Feed(object):
    """Create a feed object

    Args:
        start_date ([type]): start date of the data
        end_date ([type]): end date of the data
        price_field_name ([type]): name of the price field
    """

    def __init__(self, start_date=None, end_date=None, price_field_name="Close"):
        self.start_date = start_date
        self.end_date = end_date
        self.price_field_name = price_field_name

    def reset_feed(self):
        raise NotImplementedError

    def get_price_data(self, end_dt, start_dt=None):
        raise NotImplementedError

    def get_data(self, end_dt, start_dt=None, fields=None):
        raise NotImplementedError

    def get_data_idx(self):
        raise NotImplementedError


class CSVDataFeed(Feed):
    def __init__(self, file_name, price_field_name="Price Close", *args, **kwargs):
        super(CSVDataFeed, self).__init__(
            price_field_name=price_field_name, *args, **kwargs
        )
        self.file_name = file_name
        self.data = []
        self.reset_feed(self.start_date, self.end_date)
        self.num_assets = len(self.data.keys())

    def reset_feed(self, start_dt, end_dt):
        """resets the datafeed, i.e. pulls new data if necessary"""

        # only download new data if start and end date are not the same as before or if data is empty
        if (self.start_date != start_dt or self.end_date != end_dt) or (
            len(self.data) == 0
        ):
            data = pd.read_csv(self.file_name, index_col=0)
            data["Date"] = pd.to_datetime(
                data["Date"], format="%Y-%m-%d"
            ).dt.tz_localize(None)

            if self.start_date is None:
                self.start_date = data.Date.min().strftime("%Y-%m-%d")

            if self.end_date is None:
                self.end_date = data.Date.max().strftime("%Y-%m-%d")

            if pd.to_datetime(self.start_date) < data.Date.min():
                raise ValueError("No data available at specified start date")

            if data.Date.max() < pd.to_datetime(self.end_date):
                raise ValueError("No data available at specified end date")

            self.data = self._convert_to_dict(data)

    def get_data_idx(self):
        """gets all possible dates/indexes from the data"""

        first_df = next(iter(self.data.values()))
        return first_df.index

    def _convert_to_dict(self, price_data):
        """converts the data in df format to dict of df's, one key per asset"""

        ts_data = {}
        for ric in price_data.Instrument.unique():
            df_temp = price_data.loc[price_data.loc[:, "Instrument"] == ric, :]
            df_temp = df_temp.drop("Instrument", 1)
            df_temp = df_temp.set_index("Date")
            df_temp = df_temp.loc[self.start_date : self.end_date, :]
            ts_data[ric] = df_temp
        return ts_data

    def get_available_fields(self):
        """returns a list of all possible fields from the data"""

        return next(iter(self.data.values())).colums

    def get_price_data(self, end_dt, start_dt=None, offset=None):
        """returns price data in one dataframe, each column contains an asset"""
        """
        if start_dt is None and offset is not None:
            start_dt = (pd.to_datetime(end_dt) - timedelta(days=offset)).strftime("%Y-%m-%d")
        """
        prices = self.get_data(
            end_dt=end_dt,
            start_dt=start_dt,
            fields=self.price_field_name,
            offset=offset,
        )
        return prices

    def get_data(self, end_dt, start_dt=None, fields=None, offset=None):
        """returns data for all assets for given fields
        NOTE: Currently, only one field is allowed so that data can be returned in one DataFrame
        """

        if isinstance(fields, list):
            raise ValueError("Multiple fields not supported yet in get_data ")

        if fields is None:
            fields = self.get_available_fields()
            if len(fields) > 0:
                raise ValueError("Multiple fields not supported yet in get_data ")

        go_via_offset = False
        if start_dt is None:
            start_dt = end_dt
            if offset is not None:
                go_via_offset = True

        data_out = pd.DataFrame()
        for k, v in self.data.items():
            if go_via_offset:
                data_temp = self.data[k].loc[:end_dt, fields].iloc[-offset:].to_frame()
            else:
                data_temp = self.data[k].loc[start_dt:end_dt, fields].to_frame()
            data_temp.columns = [k]
            data_out = pd.concat([data_out, data_temp], axis=1)

        return data_out


# %%
class BaseDataFeed(object):
    # initialize datafeed
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.num_tickers = len(tickers)
        self.start_date = start_date
        self.end_date = end_date
        self.df = self.get_data()

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
        price_data = (
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
        # close should be similar to adjusted close
        price_data["close"] = price_data["adj_close"]
        price_data["date"] = pd.to_datetime(price_data["date"])
        # convert column to string
        price_data["ticker"] = price_data["ticker"].astype(str)
        price_data = price_data.dropna()
        price_data = price_data.reset_index(drop=True)
        print("Shape of DataFrame: ", price_data.shape)

        price_data = price_data.sort_values(by=["date", "ticker"])
        price_data.set_index(["date", "ticker"], inplace=True)
        return price_data


# %%
class StooqDataFeed(BaseDataFeed):
    # inherit from BaseDataFeed
    def __init__(self, tickers, start_date, end_date):
        super().__init__(tickers, start_date, end_date)

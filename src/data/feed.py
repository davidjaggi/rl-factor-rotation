# %%
import pandas as pd
import pandas_datareader.data as web


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

    def reset_feed(self, start_dt, end_dt) -> dict:
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

    def _convert_to_dict(self, price_data) -> dict:
        """converts the data in df format to dict of df's, one key per asset"""

        ts_data = {}
        for ric in price_data.Instrument.unique():
            df_temp = price_data.loc[price_data.loc[:, "Instrument"] == ric, :]
            df_temp = df_temp.drop("Instrument", 1)
            df_temp = df_temp.set_index("Date")
            df_temp = df_temp.loc[self.start_date: self.end_date, :]
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
class StooqDataFeed(Feed):
    # initialize datafeed
    def __init__(self, tickers, price_field_name="Close", *args, **kwargs):
        super(StooqDataFeed, self).__init__(
            price_field_name=price_field_name, *args, **kwargs
        )
        self.tickers = tickers
        self.data = []
        self.reset_feed(self.start_date, self.end_date)
        self.num_assets = len(self.data.keys())

    def reset_feed(self, start_dt, end_dt):
        """resets the datafeed, i.e. pulls new data if necessary"""

        # only download new data if start and end date are not the same as before or if data is empty
        if (self.start_date != start_dt or self.end_date != end_dt) or (
                len(self.data) == 0
        ):
            data = pd.DataFrame()
            for i in range(len(self.tickers)):
                # download each stock by itself
                df = web.DataReader(self.tickers[i], "stooq", start_dt, end_dt)
                df.reset_index(inplace=True)
                df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d").dt.tz_localize(None)
                df["Instrument"] = self.tickers[i]
                data = data.append(df)

            if self.start_date is None:
                self.start_date = data.Date.min().strftime("%Y-%m-%d")

            if self.end_date is None:
                self.end_date = data.Date.max().strftime("%Y-%m-%d")

            if pd.to_datetime(self.start_date) < data.Date.min():
                pass
                # TODO how can we solve this?
                # let's say we select the start date as sunday
                # there will be no data on sunday so the start date will be smaller than the first date
                # raise ValueError("No data available at specified start date")

            if data.Date.max() < pd.to_datetime(self.end_date):
                pass
                # raise ValueError("No data available at specified end date")

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
            df_temp = df_temp.loc[self.start_date: self.end_date, :]
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

    def get_data(self, end_dt, start_dt=None, offset=None):
        """return price data from yahoo finance"""

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
if __name__ == "__main__":
    feed = StooqDataFeed(["AAPL", "MSFT", "GOOG"], start_date="2017-01-01", end_date="2018-01-01")

# %%
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pandas_datareader.data as web

from .generate_paths import generate_paths


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

    def reset(self, start_dt, end_dt):
        raise NotImplementedError

    def get_price_data(self, end_dt, start_dt=None):
        raise NotImplementedError

    def get_return_data(self, end_dt, start_dt=None):
        raise NotImplementedError

    def get_data(self, end_dt, start_dt=None, fields=None):
        raise NotImplementedError

    def get_data_idx(self):
        raise NotImplementedError


class CSVDataFeed(Feed):
    def __init__(self, file_name, price_field_name="price", *args, **kwargs):
        super(CSVDataFeed, self).__init__(
            price_field_name=price_field_name, *args, **kwargs
        )
        self.file_name = file_name
        self.reset(self.start_date, self.end_date)
        self.num_assets = len(self.data.keys())
        self.dates = self.get_dates()

    def reset(self, start_dt, *args, **kwargs):
        """resets the datafeed, i.e. pulls new data if necessary"""

        # only download new data if start and end date are not the same as before or if data is empty
        if (self.start_date != start_dt or self.end_date != kwargs.get('end_date', None)) or not hasattr(self, 'data'):

            data = pd.read_csv(self.file_name)
            data["Date"] = pd.to_datetime(
                data["Date"], format="%Y%m%d"
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
        self.dt = pd.to_datetime(start_dt, format="%Y-%m-%d")

    def get_data_idx(self):
        """gets all possible dates/indexes from the data"""

        first_df = next(iter(self.data.values()))
        return first_df.index

    def _convert_to_dict(self, price_data) -> dict:
        """converts the data in df format to dict of df's, one key per asset"""

        ts_data = {}
        for ric in price_data.Instrument.unique():
            df_temp = price_data.loc[price_data.loc[:, "Instrument"] == ric, :]
            # drop Instrument column
            df_temp = df_temp.drop(columns=["Instrument"])
            df_temp = df_temp.set_index("Date")
            df_temp = df_temp.loc[self.start_date: self.end_date, :]
            ts_data[ric] = df_temp
        return ts_data

    def get_available_fields(self):
        """returns a list of all possible fields from the data"""

        return next(iter(self.data.values())).columns

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

    def get_prices_snapshot(self, idx):
        date = self.dates[idx]
        prices = {}
        for idx, (asset, price) in enumerate(self.data.items()):
            prices[asset] = self.data[asset].loc[self.dt]

        # And update the dt to the next prices snapshot
        dt_idx = self.data[list(self.data.keys())[0]].index.get_loc(date)
        self.dt = self.data[list(self.data.keys())[0]].index[dt_idx + 1]
        prices = {k: v['price'] for k, v in prices.items()}
        return prices

    def get_dates(self):
        dates = []
        for idx, (asset, price) in enumerate(self.data.items()):
            dates.append(self.data[asset].index)
        # return ordered dates
        return sorted(set(dates[0]).intersection(*dates))

    def get_observations(self, idx, offset=5):
        date = self.dates[idx]
        prices = {}
        for idx, (asset, price) in enumerate(self.data.items()):
            # take date and offset days before
            prices[asset] = self.data[asset].loc[date - timedelta(days=offset - 1):date]
            # fill missing dates with 0
            prices[asset] = prices[asset].reindex(pd.date_range(date - timedelta(days=offset - 1), date), fill_value=0)

        prices_array = [prices[asset]["price"].values for asset in prices.keys()]
        return prices_array

    def get_idx(self, date):
        dt = pd.to_datetime(date)
        return self.dates.index(dt)

    def get_date(self, idx):
        return self.dates[idx]


class GBMtwoAssetsFeed(object):

    def __init__(self, gbmInput:dict, num_assets:int, start_date=None, end_date=None, price_field_name="Close"):
        self.start_date = start_date
        self.end_date = end_date
        self.price_field_name = price_field_name

        if datetime.strptime(start_date,"%Y-%m-%d") > datetime.strptime(end_date,"%Y-%m-%d"):
            raise Exception(f"start date: {start_date} can't be older than end date!")
        else:
            self.num_assets = num_assets
            self.gbmSettings = gbmInput

        if self.checkGBMInput():
            self.data = []
            self.reset(self.start_date, self.end_date)

    def checkGBMInput(self) -> bool:
        necessaryKeys = ['StartingPrice','drift','vola','correlation']

        if not all(key in self.gbmSettings for key in necessaryKeys):
            raise KeyError

        for key in necessaryKeys:
            if key == 'correlation':
                if not (isinstance(self.gbmSettings[key], np.matrix) or self.gbmSettings[key].shape == (self.num_assets,self.num_assets)):
                    raise Exception("TypeError or Shape Error Correlation Matrix should be np.matrix() or the dimensions do not add up.")
            else:
                if not (isinstance(self.gbmSettings[key],(np.ndarray, np.generic)) or len(self.gbmSettings[key]) == self.num_assets):
                    raise TypeError
        return True

    def reset(self, start_dt, end_dt) -> dict:
        """resets the datafeed, i.e. pulls new data if necessary"""

        # only download new data if start and end date are not the same as before or if data is empty
        if (self.start_date != start_dt or self.end_date != end_dt) or (
                len(self.data) == 0
        ):
            data = generate_paths(
                spot=self.gbmSettings['StartingPrice'],
                drift=self.gbmSettings['drift'],
                sigma=self.gbmSettings['vola'],
                correlation=self.gbmSettings['correlation'],
                start_date=start_dt,
                end_date=end_dt,
                dt=1)

            if self.start_date is None:
                self.start_date = data.index.min().strftime("%Y-%m-%d")

            if self.end_date is None:
                self.end_date = data.index.max().strftime("%Y-%m-%d")

            if pd.to_datetime(self.start_date) < data.index.min():
                raise ValueError("No data available at specified start date")

            if data.index.max() < pd.to_datetime(self.end_date):
                raise ValueError("No data available at specified end date")

            self.data = self._convert_to_dict(data)

    def _convert_to_dict(self,dataDf:pd.DataFrame) -> dict:
        data = {}
        for col in dataDf.columns:
            tempDF = pd.DataFrame(index=dataDf.index, columns=[self.price_field_name], data=dataDf[col].values)
            tempDF.index.name = 'Date'
            data[col] = tempDF
        return data

    def get_price_data(self, end_dt, start_dt=None, offset=None):
        """returns price data in one dataframe, each column contains an asset"""

        if start_dt is None and offset is not None:
            start_dt = (pd.to_datetime(end_dt) - timedelta(days=offset)).strftime("%Y-%m-%d")

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

    def get_data_idx(self):
        """gets all possible dates/indexes from the data"""

        first_df = next(iter(self.data.values()))
        return first_df.index

    def get_available_fields(self):
        """returns a list of all possible fields from the data"""

        return next(iter(self.data.values())).colums



# %%
class StooqDataFeed(Feed):
    # initialize datafeed
    def __init__(self, tickers, price_field_name="Close", *args, **kwargs):
        super(StooqDataFeed, self).__init__(
            price_field_name=price_field_name, *args, **kwargs
        )
        self.tickers = tickers
        self.data = []
        self.reset(self.start_date, self.end_date)
        self.num_assets = len(self.data.keys())

    def reset(self, start_dt, end_dt):
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
# if __name__ == "__main__":
#     try:
#         feedDataFeed = StooqDataFeed(["AAPL", "MSFT", "GOOG"], start_date="2017-01-01", end_date="2018-01-01")
#     except Exception as e:
#         print(e)
#
#     try:
#         feed = CSVDataFeed('C:\\Users\\grbi\\PycharmProjects\\rl-factor-rotation\\data\\example_data.csv')
#     except Exception as e:
#         print(e)
#
#     try:
#         feed = CSVDataFeed('C:\\Users\\grbi\\PycharmProjects\\rl-factor-rotation\\data\\example_data.csv')
#     except Exception as e:
#         print(e)
#
#     gbmInput = {'StartingPrice': np.array([100, 100]),
#                 'drift': np.array([0.05 / np.sqrt(260), 0.1 / np.sqrt(260)]),
#                 'vola': np.array([0.1 / np.sqrt(260), 0.2 / np.sqrt(260)]),
#                 'correlation': np.matrix([[1, 0.3], [0.3, 1]])}
#
#     feed = GBMtwoAssetsFeed(gbmInput=gbmInput, num_assets=2, end_date="2020-12-31", start_date="2018-12-31")
#     print(feed)

# %%
from pandas_datareader import data
import pandas as pd
# %%
def get_data(tickers, start_date, end_date):
    '''
    Downloads data from public sources.

            Parameters:
                    tickers (list): Tickers for which to download data
                    start_date (str): Start date in format "YYYY-MM-DD"
                    end_date (str): End date in format "YYYY-MM-DD"

            Returns:
                    price_data (DataFrame): price data which was pulled
    '''

    # get close prices
    price_data = data.DataReader(tickers, 'stooq', start_date, end_date)['Close']

    # fill with all business days and include nan's where no data is available
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
    price_data = price_data.reindex(all_weekdays)
    price_data = price_data.fillna(method='ffill')

    return price_data
# %%

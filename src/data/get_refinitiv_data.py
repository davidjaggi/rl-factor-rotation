from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import eikon as ek


MAX_DATA_SIZE = 50000
ek.set_app_key("<< INSERT YOUR KEY HERE >>")


def get_timeseries(rics, fields, start_date, end_date, date_ind=True, transform=False):
    """ Get time series data for a list of RICs """

    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    d = end_date_dt - start_date_dt
    splits = np.ceil(d.days * len(fields) * len(rics) / MAX_DATA_SIZE)
    jump_dates = np.ceil(d.days / splits)

    all_ts_data = pd.DataFrame()
    strt = start_date_dt
    ed = strt + timedelta(jump_dates)
    while ed < end_date_dt:
        ts_request = [f + "(SDate='" + strt.strftime('%Y-%m-%d') + "', EDate='" + ed.strftime('%Y-%m-%d') + "')"
                      for f in fields]
        if date_ind:
            ts_request.insert(0, ts_request[0] + ".date")
        df_prices_new, err = ek.get_data(rics, ts_request)
        all_ts_data = all_ts_data.append(df_prices_new)
        strt = ed
        ed = strt + timedelta(jump_dates)

    ed = end_date_dt
    ts_request = [f + "(SDate='" + strt.strftime('%Y-%m-%d') + "', EDate='" + ed.strftime('%Y-%m-%d') + "')"
                  for f in fields]
    if date_ind:
        ts_request.insert(0, ts_request[0] + ".date")
    df_prices_new, err = ek.get_data(rics, ts_request)
    all_ts_data = all_ts_data.append(df_prices_new)

    # now take this out of the list into one large DataFrame
    df_all = all_ts_data.drop_duplicates()
    df_all['Date'].replace('', np.nan, inplace=True)
    df_all.dropna(subset=['Date'], inplace=True)

    # transform the output into dict if necessary
    if transform:
        ts_data = {}
        for ric in df_all.Instrument.unique():
            df_temp = df_all.loc[df_all.loc[:, 'Instrument'] == ric, :]
            ts_data[ric] = df_temp
        return ts_data
    else:
        return df_all


if __name__ == "__main__":

    # This is an example for downloading Google stock OHLCV prices...
    all_rics = ['GOOGL.O']
    price_flds = ['TR.PriceOpen', 'TR.PriceHigh', 'TR.PriceLow', 'TR.PriceClose', 'TR.Volume']
    prices = get_timeseries(rics=all_rics,
                            fields=price_flds,
                            start_date="2015-12-31",
                            end_date="2020-12-31")
    # prices["Price Close"].plot()

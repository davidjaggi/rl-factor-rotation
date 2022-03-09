# %%
from datetime import datetime

import pandas as pd
import numpy as np

from get_refinitiv_data import get_timeseries

"""
generates Final DataSet for UseCase Test:
"""


def getETFData(all_rics: list = ['MTUM.K', 'VLUE.K', 'USMV.K', 'QUAL.K', 'SIZE.K']):
    names = ['momentum', 'value', 'lowVola', 'quality', 'size']
    df = pd.DataFrame(index=pd.date_range("2015-12-31", end=datetime.now().strftime("%Y-%m-%d"), tz='UTC'))

    price_flds = ['TR.PriceClose']
    for counter in range(0, len(all_rics)):
        df_temp = get_timeseries(rics=all_rics[counter],
                                 fields=price_flds,
                                 start_date="2015-12-31",
                                 end_date=datetime.now().strftime("%Y-%m-%d"))

        df_temp = df_temp.set_index(['Date'])
        df_temp.index = pd.to_datetime(df_temp.index)
        df_temp = df_temp[['Price Close']]
        df_temp.columns = [names[counter]]
        df = pd.merge(df, df_temp, left_index=True, right_index=True, how='left')
    df = df.dropna()
    return df


def readBloomiData() -> pd.DataFrame():
    return pd.read_excel("C:/Users/grbi/PycharmProjects/rl-factor-rotation/data/MSCI_Indices_Numeric.xlsx",
                         sheet_name='data', index_col=0)


if __name__ == '__main__':
    etfs = getETFData()
    bbdata = readBloomiData()
    etfs = etfs.reset_index()
    etfs['index'] = etfs['index'].apply(lambda x: pd.to_datetime(x).date())
    etfs = etfs.set_index('index')

    # calc Rets
    etfrets = etfs.apply(lambda x: np.log(x / x.shift(1)))
    bbrets = bbdata.apply(lambda x: np.log(x / x.shift(1)))
    bbrets.index = pd.to_datetime(bbrets.index)
    bbrets = bbrets.sort_index(ascending=False)

    df_final = pd.DataFrame(index=pd.date_range(start=min([min(etfrets.index), min(bbrets.index)], ),
                                                end=max([max(etfrets.index), max(bbrets.index)])))
    df_final = pd.merge(df_final, etfs, left_index=True, right_index=True, how='left')
    df_final = df_final.sort_index(ascending=False)
    df_final.to_excel("tempSave.xlsx")  # issue with <NA> Type -> Never seen before ..
    df_final = pd.read_excel("tempSave.xlsx", index_col=0)

    for col in df_final.columns:
        if col == 'size':  # not downloaded yet.
            continue

        naSeries = df_final.loc[:, col].isna()
        for ind in range(100, len(df_final.index)):
            start = df_final.index[ind - 1]
            end = df_final.index[ind]

            if naSeries.loc[end.strftime("%Y-%m-%d")]:
                try:
                    df_final.loc[end, col] = df_final.loc[start, col] / (1 + bbrets.loc[end, col])
                except:
                    df_final.loc[end, col] = df_final.loc[start, col]

        # df_final.to_excel("SampleData.xlsx")
    # for Feed:
    a = df_final.unstack()
    a = a.reset_index()
    a.columns = ['Instrument', 'Date', 'Price']
    a.to_csv('ETFSample.csv')

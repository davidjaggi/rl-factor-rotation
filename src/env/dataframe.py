import pandas as pd
import datetime
import random
from abc import ABC


def consolidation(hist_dict):
    hist_dict = hist_dict

    df_benchmark = pd.DataFrame()
    df_rl = pd.DataFrame()
    df_historical = pd.DataFrame()

    timestamp_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('timestamp'))
    cash_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('cash'))
    positions_benchmark1 = pd.DataFrame(hist_dict.get('benchmark').get('positions'))

    timestamp_rl = pd.DataFrame(hist_dict.get('rl').get('timestamp'))
    cash_rl = pd.DataFrame(hist_dict.get('rl').get('cash'))
    positions_rl1 = pd.DataFrame(hist_dict.get('rl').get('positions'))

    historical_prices = pd.DataFrame()
    col_assets = list(hist_dict['historical_asset_prices'][0]['prices'].keys())

    for i in hist_dict['historical_asset_prices']:
        prices = pd.DataFrame(i.get('prices'), index=[i.get('timestamp')])
        historical_prices = historical_prices.append(prices, ignore_index=False)

    df_benchmark['date'] = timestamp_benchmark
    for i in positions_benchmark1.columns:
        df_benchmark[i + '_bm'] = positions_benchmark1[i]
    df_benchmark['cash_bm'] = cash_benchmark
    df_benchmark['date'] = pd.to_datetime(df_benchmark['date'])

    df_rl['date'] = timestamp_rl
    for i in positions_rl1.columns:
        df_rl[i + '_rl'] = positions_rl1[i]
    df_rl['cash_rl'] = cash_rl
    df_rl['date'] = pd.to_datetime(df_rl['date'])

    for i in historical_prices.columns:
        df_historical[i + '_hist'] = historical_prices[i]
    df_historical.reset_index(inplace=True)
    df_historical.rename(columns={'index': 'date'}, inplace=True)
    consolidated = df_benchmark.merge(df_rl, on='date', how='left')
    consolidated = consolidated.merge(df_historical, on='date', how='left')
    consolidated = consolidated.set_index('date')

    return consolidated




'''
class Con_DataFrame(ABC):

    def __init__(self, hist_dict):
        self.hist_dict = hist_dict

    def consolidation(self):
        df_benchmark = pd.DataFrame()
        df_rl = pd.DataFrame()
        df_historical = pd.DataFrame()

        timestamp_benchmark = pd.DataFrame(self.hist_dict.get('benchmark').get('timestamp'))
        cash_benchmark = pd.DataFrame(self.hist_dict.get('benchmark').get('cash'))
        assets_benchmark = pd.DataFrame(self.hist_dict.get('benchmark').get('positions'))

        timestamp_rl = pd.DataFrame(self.hist_dict.get('rl').get('timestamp'))
        cash_rl = pd.DataFrame(self.hist_dict.get('rl').get('cash'))
        assets_rl = pd.DataFrame(self.hist_dict.get('rl').get('positions'))

        historical_prices = pd.DataFrame(self.hist_dict.get('historical_asset_prices'))

        df_benchmark['date'] = timestamp_benchmark
        for i in assets_benchmark.columns:
            df_benchmark[i+'_bm'] = assets_benchmark[i]
        df_benchmark['cash_bm'] = cash_benchmark
        df_benchmark['date'] = pd.to_datetime(df_benchmark['date'])


        df_rl['date'] = timestamp_rl
        for i in assets_rl.columns:
            df_rl[i+'_rl'] = assets_rl[i]
        df_rl['cash_rl'] = cash_rl
        df_rl['date'] = pd.to_datetime(df_rl['date'])


        for i in historical_prices.columns:
            df_historical[i+'_hist'] = historical_prices[i]
        df_historical['date'] = pd.to_datetime(df_benchmark['date'])


        self.consolidated = df_benchmark.merge(df_rl, on='date', how='left')
        self.consolidated = self.together.merge(df_historical, on='date', how='left')

        return self.consolidated

    def last_entry(self):
        return self.consolidated[-1]
'''
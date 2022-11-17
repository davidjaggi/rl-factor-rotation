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
    positions_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('positions'))
    portfolio_values_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('portfolio_values'))
    portfolio_weights_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('portfolio_weights'))

    timestamp_rl = pd.DataFrame(hist_dict.get('rl').get('timestamp'))
    cash_rl = pd.DataFrame(hist_dict.get('rl').get('cash'))
    positions_rl = pd.DataFrame(hist_dict.get('rl').get('positions'))
    portfolio_values_rl = pd.DataFrame(hist_dict.get('benchmark').get('portfolio_values'))
    portfolio_weights_rl = pd.DataFrame(hist_dict.get('benchmark').get('portfolio_weights'))

    historical_prices = pd.DataFrame()
    col_assets = list(hist_dict['historical_asset_prices'][0]['prices'].keys())

    for i in hist_dict['historical_asset_prices']:
        prices = pd.DataFrame(i.get('prices'), index=[i.get('timestamp')])
        historical_prices = historical_prices.append(prices, ignore_index=False)

    list1 = list(positions_benchmark.columns)
    list1.append('total_value')

    df_benchmark['date'] = timestamp_benchmark
    for i in positions_benchmark.columns:
        df_benchmark[i + '_position_bm'] = positions_benchmark[i]
        df_benchmark[i + '_weight_bm'] = portfolio_weights_benchmark[i]
    for i in list1:
        df_benchmark[i + '_portfolio_bm'] = portfolio_values_benchmark[i]

    df_benchmark['cash_bm'] = cash_benchmark
    df_benchmark['date'] = pd.to_datetime(df_benchmark['date'])

    df_rl['date'] = timestamp_rl
    for i in positions_rl.columns:
        df_rl[i + '_position_rl'] = positions_rl[i]
        df_rl[i + '_weight_rl'] = portfolio_weights_rl[i]
    for i in list1:
        df_rl[i + '_portfolio_rl'] = portfolio_values_rl[i]

    df_rl['cash_rl'] = cash_rl
    df_rl['date'] = pd.to_datetime(df_rl['date'])

    for i in historical_prices.columns:
        df_historical[i + '_price_hist'] = historical_prices[i]
    df_historical.reset_index(inplace=True)
    df_historical.rename(columns={'index': 'date'}, inplace=True)
    consolidated = df_benchmark.merge(df_rl, on='date', how='left')
    consolidated = consolidated.merge(df_historical, on='date', how='left')
    consolidated = consolidated.set_index('date')

    return consolidated


def splitting(df):

    column_headers = list(df.columns.values)

    list_bm = [
        item for item in column_headers
        if item[-1] == 'm'
    ]

    list_rl = [
        item for item in column_headers
        if item[-1] == 'l'
    ]

    list_hist = [
        item for item in column_headers
        if item[-1] == 't'
    ]

    position_bm = [
        item for item in column_headers
        if item[-1] == 'm' and item[-4] == 'n'
    ]

    position_rl = [
        item for item in column_headers
        if item[-1] == 'l' and item[-4] == 'n'
    ]

    weight_bm = [
        item for item in column_headers
        if item[-1] == 'm' and item[-4] == 't'
    ]

    weight_rl = [
        item for item in column_headers
        if item[-1] == 'l' and item[-4] == 't'
    ]

    value = [
        item for item in column_headers
        if item[-4] == 'o'
    ]

    cash = [
        item for item in column_headers
        if item[-4] == 'h' and item[-1] != 't'
    ]


    df_position_bm = df[position_bm].copy(deep=True)
    df_position_rl = df[position_rl].copy(deep=True)

    df_weight_bm = df[weight_bm].copy(deep=True)
    df_weight_rl = df[weight_rl].copy(deep=True)

    df_bm = df[list_bm].copy(deep=True)
    df_rl = df[list_rl].copy(deep=True)
    df_hist = df[list_hist].copy(deep=True)
    df_cash = df[cash].copy(deep=True)
    df_value = df[value].copy(deep=True)

    return df, df_bm, df_rl, df_hist, df_cash, df_value, df_position_bm, df_position_rl, df_weight_bm, df_weight_rl



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

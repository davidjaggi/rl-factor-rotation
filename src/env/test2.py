from datetime import date

import pandas as pd
from server.Simple_Test_Script import ret

hist_dict = ret(125, 10000, date(2018, 12, 31), date(2020, 12, 31), 1, 5, 0.05 / 100, 'equally_weighted',
                '/example_data.csv')

'''
hist_dict = {'benchmark':
                 {'timestamp':
                      [Timestamp('2018-12-31 00:00:00'),
                       Timestamp('2019-01-02 00:00:00')],
                  'positions':
                      [{'GOOGL.O': 47, 'AAPL.O': 1261},
                       {'GOOGL.O': 47, 'AAPL.O': 1261}],
                  'cash':
                      [305.40750000000844, 305.40750000000844],
                  'portfolio_values':
                      [{'GOOGL.O': 49113.12, 'AAPL.O': 49727.535, 'total_value': 98840.655},
                       {'GOOGL.O': 49113.12, 'AAPL.O': 49727.535, 'total_value': 98840.655}],
                  'portfolio_weights':
                      [{'GOOGL.O': 0.4968918912971591, 'AAPL.O': 0.503108108702841, 'total_value': 1.0},
                       {'GOOGL.O': 0.4968918912971591, 'AAPL.O': 0.503108108702841, 'total_value': 1.0}]},
             'rl':
                 {'timestamp':
                      [Timestamp('2018-12-31 00:00:00'),
                       Timestamp('2019-01-02 00:00:00')],
                  'positions':
                      [{'GOOGL.O': 47, 'AAPL.O': 1261},
                       {'GOOGL.O': 47, 'AAPL.O': 1261}],
                  'cash':
                      [305.40750000000844, 305.40750000000844],
                  'portfolio_values':
                      [{'GOOGL.O': 49113.12, 'AAPL.O': 49727.535, 'total_value': 98840.655},
                       {'GOOGL.O': 49113.12, 'AAPL.O': 49727.535, 'total_value': 98840.655}],
                  'portfolio_weights':
                      [{'GOOGL.O': 0.4968918912971591, 'AAPL.O': 0.503108108702841, 'total_value': 1.0},
                       {'GOOGL.O': 0.4968918912971591, 'AAPL.O': 0.503108108702841, 'total_value': 1.0}]},
             'historical_asset_prices':
                 [{'timestamp':
                       Timestamp('2018-12-31 00:00:00'),
                   'prices':
                       {'GOOGL.O': 1057.83, 'AAPL.O': 39.6325}},
                  {'timestamp':
                       Timestamp('2019-01-02 00:00:00'),
                   'prices':
                       {'GOOGL.O': 1027.2, 'AAPL.O': 38.7225}}]}
'''

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
df_historical.rename(columns={'index':'date'}, inplace=True)
consolidated = df_benchmark.merge(df_rl, on='date', how='left')
consolidated = consolidated.merge(df_historical,on='date',how='left')
consolidated = consolidated.set_index('date')


df = consolidated
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

value_bm = [
    item for item in column_headers
    if item[-1] == 'm' and item[-4] == 'o'
]

value_rl = [
    item for item in column_headers
    if item[-1] == 'l' and item[-4] == 'o'
]

df_position_bm = df[position_bm].copy(deep=True)
df_position_rl = df[position_rl].copy(deep=True)

df_weight_bm = df[weight_bm].copy(deep=True)
df_weight_rl = df[weight_rl].copy(deep=True)

df_value_bm = df[value_bm].copy(deep=True)
df_value_rl = df[value_rl].copy(deep=True)

df_bm = df[list_bm].copy(deep=True)
df_rl = df[list_rl].copy(deep=True)
df_hist = df[list_hist].copy(deep=True)




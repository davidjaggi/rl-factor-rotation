import pandas as pd
import datetime
import random
import threading
import time  # to simulate a real time data, time loop
import datetime

from Simple_Test_Script import ret
from pandas import Timestamp

hist_dict = ret(2)
print(hist_dict)


hist1 = {'benchmark':
             {'timestamp':
                  [Timestamp('2018-12-31 00:00:00'), Timestamp('2019-01-02 00:00:00'), Timestamp('2019-01-03 00:00:00')],
              'positions':
                  [{'GOOGL.O': 47, 'AAPL.O': 1261}, {'GOOGL.O': 47, 'AAPL.O': 1261}, {'GOOGL.O': 47, 'AAPL.O': 1261}],
              'cash':
                  [305.40750000000844, 305.40750000000844, 305.40750000000844]},
         'rl':
             {'timestamp':
                  [Timestamp('2018-12-31 00:00:00'), Timestamp('2019-01-02 00:00:00'), Timestamp('2019-01-03 00:00:00')],
              'positions':
                  [{'GOOGL.O': 47, 'AAPL.O': 1261}, {'GOOGL.O': 47, 'AAPL.O': 1261}, {'GOOGL.O': 47, 'AAPL.O': 1261}],
              'cash':
                  [305.40750000000844, 305.40750000000844, 305.40750000000844]},
         'historical_asset_prices':
             [{'timestamp': Timestamp('2018-12-31 00:00:00'), 'prices': {'GOOGL.O': 1057.83, 'AAPL.O': 39.6325}},
              {'timestamp': Timestamp('2019-01-02 00:00:00'), 'prices': {'GOOGL.O': 1027.2, 'AAPL.O': 38.7225}},
              {'timestamp': Timestamp('2019-01-03 00:00:00'), 'prices': {'GOOGL.O': 1050.67, 'AAPL.O': 35.995}}]}


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
df_historical.rename(columns={'index':'date'}, inplace=True)
consolidated = df_benchmark.merge(df_rl, on='date', how='left')
consolidated = consolidated.merge(df_historical,on='date',how='left')
consolidated = consolidated.set_index('date')

consolidated
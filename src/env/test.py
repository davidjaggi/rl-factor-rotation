#benchmark_portfolio.hist_dict['benchmark']['holdings'][-1]
from datetime import date

import pandas as pd

from src.analyzer.analyzer import Analyzer
from src.server.runner import ret

file_name = r'E:\PycharmProjects\rl-factor-rotation\data\example_factor_clean.csv'

data = pd.read_csv(file_name)
#data.columns = data.iloc[0]
data["Date"] = pd.to_datetime(data["Date"], format="%Y%m%d").dt.tz_localize(None)
data["Date"] = data['Date'].dt.date

days = 300
initial_balance = 1000000
start_date = date(2010, 12, 31)
end_date = date(2020, 12, 31)
reward_scaling = 1
obs_price_hist = 5
transaction_cost = 0.05 / 100
weighting_method = 'equally_weighted'
training_data = '/example_factor_clean.csv'
env = ret(days, initial_balance, start_date, end_date, transaction_cost, reward_scaling, obs_price_hist, weighting_method, training_data)
analyzer = Analyzer(env)
df = analyzer.data

def convert_df(df):
    return df.to_csv(index=True).encode('utf-8')

csv = convert_df(df)


import time  # to simulate a real time data, time loop
import datetime
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st
import random
#from src.env.broker import Broker
#from src.evn.dataframe import Con_DataFrame


def pltt():
    df = pd.DataFrame()

    base = datetime.datetime.today()
    days = 125
    hist_dict = {'benchmark': {'timestamp': [base - datetime.timedelta(days=x) for x in range(days)],
                               'positions': {'asset1': random.sample(range(800, 1200), days),
                                             'asset2': random.sample(range(500, 700), days),
                                             'asset3': random.sample(range(200, 350), days)},
                               'cash': random.sample(range(0, 10000), days)},
                    'rl': {'timestamp': [base - datetime.timedelta(days=x) for x in range(days)],
                           'positions': {'asset1': random.sample(range(800, 1200), days),
                                         'asset2': random.sample(range(500, 700), days),
                                         'asset3': random.sample(range(200, 350), days)},
                           'cash': random.sample(range(0, 10000), days)},
                 'historical_asset_prices': {'asset1': random.sample(range(200, 350), days),
                                             'asset2': random.sample(range(400, 550), days),
                                             'asset3': random.sample(range(600, 750), days)}}



    df_benchmark = pd.DataFrame()
    df_rl = pd.DataFrame()
    df_historical = pd.DataFrame()

    timestamp_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('timestamp'))
    cash_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('cash'))
    assets_benchmark = pd.DataFrame(hist_dict.get('benchmark').get('positions'))

    timestamp_rl = pd.DataFrame(hist_dict.get('rl').get('timestamp'))
    cash_rl = pd.DataFrame(hist_dict.get('rl').get('cash'))
    assets_rl = pd.DataFrame(hist_dict.get('rl').get('positions'))

    historical_prices = pd.DataFrame(hist_dict.get('historical_asset_prices'))

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


    together = df_benchmark.merge(df_rl, on='date', how='left')
    together = together.merge(df_historical, on='date', how='left')


    df2 = together



    # top-level filters
    #day_filter = st.selectbox("Select the day", df["asset_bm"]))

    # dataframe filter

    df2 = df2.set_index('date')
    df_bm = df2[['asset1_bm','asset2_bm','asset3_bm']].copy()
    df_rl = df2[['asset1_rl','asset2_rl','asset3_rl']].copy()
    df_hist = df2[['asset1_hist','asset2_hist','asset3_hist']].copy()



    res_bm = df_bm.div(df_bm.sum(axis=1), axis=0)
    res_rl = df_rl.div(df_rl.sum(axis=1), axis=0)
    return res_bm, res_rl, df_hist




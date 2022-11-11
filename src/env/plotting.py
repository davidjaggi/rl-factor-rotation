import time  # to simulate a real time data, time loop
import datetime
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st
import random
#from src.env.broker import Broker
#from src.evn.dataframe import Con_DataFrame


def pltt(df):
    df = df
    column_headers = list(df.columns.values)
    '''
    for i in column_headers:
        if i[-1]=='m':
            df_bm = df[[column_headers[],'asset2_bm','asset3_bm']].copy()
        elif i[-1]=='l':
            df_rl = df[['asset1_rl','asset2_rl','asset3_rl']].copy()
        elif i[-1]=='t'
            df_hist = df[['asset1_hist','asset2_hist','asset3_hist']].copy()

    #res_bm = df_bm.div(df_bm.sum(axis=1), axis=0)
    #res_rl = df_rl.div(df_rl.sum(axis=1), axis=0)
    #return res_bm, res_rl, df_hist
    '''




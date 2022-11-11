
import random
import sys

# setting path
sys.path.append('/Users/kiafarokhnia/PycharmProjects/rl-factor-rotation/')

import os
import time  # to simulate a real time data, time loop
import datetime
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import random
import plotting

from Simple_Test_Script import ret
from dataframe import consolidation

def run():
    st.set_page_config(page_title="Real-Time RL Dashboard",  page_icon="✅", layout="wide")
    # dashboard title
    st.title("RL Dashboard")
    days = st.text_input(label='Days', value=125)
    if st.button(label='run Simple Test Script'):
        hist_dict = ret(days)
        df = consolidation(hist_dict)
        st.write(df)
        res_bm, res_rl, df_hist = plotting.pltt(df)
        st.header('Benchmark holdings')
        st.area_chart(res_bm)
        st.header('RL Agent holdings')
        st.area_chart(res_rl)
        st.header('Historical asset prices')
        st.line_chart(df_hist)

if __name__ == '__main__':
    run()

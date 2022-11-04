
import random

import os
import time  # to simulate a real time data, time loop
import datetime
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
import random
import plotting


def run():
    st.set_page_config(page_title="Real-Time RL Dashboard",  page_icon="✅", layout="wide")
    # dashboard title
    st.title("Hello")
    if st.button(label='run Simple Test Script'):
        os.system('python ....Simple_Test_script.py')
        res_bm, res_rl, df_hist = plotting.pltt()
        st.header('Benchmark holdings')
        st.area_chart(res_bm)
        st.header('RL Agent holdings')
        st.area_chart(res_rl)
        st.header('Historical asset prices')
        st.line_chart(df_hist)

if __name__ == '__main__':
    run()

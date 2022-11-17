# %%
import sys

# setting path
sys.path.append('/Users/kiafarokhnia/PycharmProjects/rl-factor-rotation/')

from datetime import date
import streamlit as st  # 🎈 data web app development

from src.server.runner import ret
from src.env.dataframe import consolidation
from src.env.dataframe import splitting


def run():
    st.set_page_config(page_title="Real-Time RL Dashboard", page_icon="✅", layout="wide")
    # dashboard title
    st.title("RL Dashboard")
    days = st.text_input(label='Days', value=125)
    initial_balance = st.text_input(label='Initial balance', value=10000)
    start_date = st.date_input(label='Start date', value=date(2018, 12, 31))
    end_date = st.date_input(label='End date', value=date(2020, 12, 31))
    reward_scaling = st.number_input(label='Reward scaling', value=1, step = 1)
    obs_price_hist = st.number_input(label='Observation price history', value=5, step=1)
    transaction_cost = float(st.text_input(label='Transaction costs in %', value=0.05))/100
    weighting_method = st.selectbox(label='Weighting method', options = ['equally_weighted'])
    training_data = st.selectbox(label='Training data', options=['/example_data.csv'])



    if st.button(label='run Simple Test Script'):
        hist_dict = ret(days, initial_balance, start_date, end_date, transaction_cost, reward_scaling, obs_price_hist, weighting_method, training_data)
        df = consolidation(hist_dict)

        def convert_df(df):
            return df.to_csv(index=True).encode('utf-8')

        csv = convert_df(df)

        st.download_button(
            "Press to Download",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
        )
        st.write(df)

        df, df_bm, df_rl, df_hist, df_cash, df_value, df_position_bm, \
        df_position_rl, df_weight_bm, df_weight_rl = splitting(df)

        st.header('Benchmark holdings')
        st.line_chart(df_position_bm)

        st.header('RL Agent holdings')
        st.line_chart(df_position_rl)

        st.header('Benchmark weights')
        st.area_chart(df_weight_bm)

        st.header('RL weights')
        st.area_chart(df_weight_rl)

        st.header('Portfolio value')
        st.line_chart(df_value)

        st.header('Cash positions')
        st.line_chart(df_cash)

        st.header('Historical asset prices')
        st.line_chart(df_hist)

if __name__ == '__main__':
    run()

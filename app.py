# %%
from datetime import date

import streamlit as st

from src.analyzer.analyzer import Analyzer
from src.server.runner import ret


def run():
    st.set_page_config(page_title="Real-Time RL Dashboard", page_icon="✅", layout="wide")
    # dashboard title
    st.title("RL Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        days = st.text_input(label='Days', value=125)
        initial_balance = st.text_input(label='Initial balance', value=10000)
        start_date = st.date_input(label='Start date', value=date(2018, 12, 31))
        end_date = st.date_input(label='End date', value=date(2020, 12, 31))
    with col2:
        reward_scaling = st.number_input(label='Reward scaling', value=1, step=1)
        obs_price_hist = st.number_input(label='Observation price history', value=5, step=1)
        transaction_cost = float(st.text_input(label='Transaction costs in %', value=0.05)) / 100
        weighting_method = st.selectbox(label='Weighting method', options=['equally_weighted'])
    training_data = st.selectbox(label='Training data', options=['/example_factor_clean.csv', '/example_data.csv'])

    if st.button(label='Run Script'):
        env = ret(days, initial_balance, start_date, end_date, transaction_cost, reward_scaling, obs_price_hist,
                  weighting_method, training_data)
        analyzer = Analyzer(env)
        df = analyzer.data
        df_compare = analyzer.compare()

        def convert_df(df):
            return df.to_csv(index=True).encode('utf-8')

        csv = convert_df(df)
        # allow to download data from stramlit
        st.download_button(
            "Press to Download",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv'
        )
        with col1:
            st.header('Benchmark holdings')
            st.line_chart(analyzer.get_positions("benchmark"))

        with col2:
            st.header('RL Agent holdings')
            st.line_chart(analyzer.get_positions("rl"))

        with col1:
            st.header('Benchmark weights')
            st.area_chart(analyzer.get_weights("benchmark"))

        with col2:
            st.header('RL weights')
            st.area_chart(analyzer.get_weights("rl"))

        with col1:
            st.header('Benchmark ideal weights')
            st.area_chart(analyzer.get_ideal_weights("benchmark"))

        with col2:
            st.header('RL ideal weights')
            st.area_chart(analyzer.get_ideal_weights("rl"))

        with col1:
            st.header('Portfolio value benchmark')
            st.line_chart(analyzer.get_values("benchmark"))

        with col2:
            st.header('Portfolio value RL')
            st.line_chart(analyzer.get_values("rl"))

        with col1:
            st.header('Cash position benchmark')
            st.line_chart(analyzer.get_cash("benchmark"))
        with col2:
            st.header('Cash position RL')
            st.line_chart(analyzer.get_cash("rl"))

        with col1:
            st.header('Reward')
            st.line_chart(analyzer.get_rewards())
        with col2:
            st.header('Actions')
            st.line_chart(analyzer.get_actions())

        with col1:
            st.header('Historical asset prices')
            st.line_chart(analyzer.get_prices())

        with col2:
            st.header('Comparison')
            st.line_chart(df_compare[[col for col in df_compare.columns if "diff" in col[1]]])

        csv2 = convert_df(df_compare)
        st.download_button(
            "Press to Download",
            csv2,
            "file.csv",
            "text/csv",
            key='download-csv2'
        )
if __name__ == '__main__':
    run()
from abc import ABC

import pandas as pd


class Analyzer(ABC):
    def __init__(self, env):
        self.env = env
        self.broker = env.broker
        self.data = self._consolidation(env.broker.hist_dict)

    def _consolidation(self, hist_dict):
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
        portfolio_values_rl = pd.DataFrame(hist_dict.get('rl').get('portfolio_values'))
        portfolio_weights_rl = pd.DataFrame(hist_dict.get('rl').get('portfolio_weights'))

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

    def _splitting(self, df):

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


    def _compare(self, df):

        weight_google_bm = []
        weight_apple_bm = []

        weight_google_rl = []
        weight_apple_rl = []

        tot_val_port_bm = []
        tot_val_port_rl = []

        diff_weight_google_bm = []
        diff_weight_apple_bm = []

        diff_weight_google_rl = []
        diff_weight_apple_rl = []

        diff_port_val_bm = []
        diff_port_val_rl = []

        for step in range(len(df['date'])):
            google_pos_bm = df['GOOGL.O_position_bm'].iloc[step]
            apple_pos_bm = df['AAPL.O_position_bm'].iloc[step]

            google_pos_rl = df['GOOGL.O_position_rl'].iloc[step]
            apple_pos_rl = df['AAPL.O_position_rl'].iloc[step]

            google_hist = df['GOOGL.O_price_hist'].iloc[step]
            apple_hist = df['AAPL.O_price_hist'].iloc[step]

            cash_bm = df['cash_bm'].iloc[step]
            cash_rl = df['cash_rl'].iloc[step]

            google_weight_bm = df['GOOGL.O_weight_bm'].iloc[step]
            apple_weight_bm = df['AAPL.O_weight_bm'].iloc[step]

            google_weight_rl = df['GOOGL.O_weight_rl'].iloc[step]
            apple_weight_rl = df['AAPL.O_weight_rl'].iloc[step]

            google_portfolio_bm = df['GOOGL.O_portfolio_bm'].iloc[step]
            apple_portfolio_bm = df['AAPL.O_portfolio_bm'].iloc[step]

            google_portfolio_rl = df['GOOGL.O_portfolio_rl'].iloc[step]
            apple_portfolio_rl = df['AAPL.O_portfolio_rl'].iloc[step]

            total_value_portfolio_bm = df['total_value_portfolio_bm'].iloc[step]
            total_value_portfolio_rl = df['total_value_portfolio_rl'].iloc[step]

            weight_google_bm.append(
                (google_pos_bm * google_hist) / (google_pos_bm * google_hist + apple_pos_bm * apple_hist + cash_bm))
            weight_apple_bm.append(
                (apple_pos_bm * apple_hist) / (google_pos_bm * google_hist + apple_pos_bm * apple_hist + cash_bm))

            weight_google_rl.append(
                (google_pos_rl * google_hist) / (google_pos_rl * google_hist + apple_pos_rl * apple_hist + cash_rl))
            weight_apple_rl.append(
                (apple_pos_rl * apple_hist) / (google_pos_rl * google_hist + apple_pos_rl * apple_hist + cash_rl))

            tot_val_port_bm.append(google_pos_bm * google_hist + apple_pos_bm * apple_hist + cash_bm)
            tot_val_port_rl.append(google_pos_rl * google_hist + apple_pos_rl * apple_hist + cash_rl)

            diff_weight_google_bm.append((weight_google_bm[step] - google_weight_bm) / google_weight_bm * 100)
            diff_weight_apple_bm.append((weight_apple_bm[step] - apple_weight_bm) / apple_weight_bm * 100)

            diff_weight_google_rl.append((weight_google_rl[step] - google_weight_rl) / google_weight_rl * 100)
            diff_weight_apple_rl.append((weight_apple_rl[step] - apple_weight_rl) / apple_weight_rl * 100)

            diff_port_val_bm.append((tot_val_port_bm[step] - total_value_portfolio_bm) / total_value_portfolio_bm * 100)
            diff_port_val_rl.append((tot_val_port_rl[step] - total_value_portfolio_rl) / total_value_portfolio_rl * 100)

        data_tuples = list(
            zip(df['date'], weight_google_bm, weight_apple_bm, weight_google_rl, weight_apple_rl, tot_val_port_bm,
                tot_val_port_rl, diff_weight_google_bm, diff_weight_apple_bm, diff_weight_google_rl,
                diff_weight_apple_rl, diff_port_val_bm, diff_port_val_rl))

        df_comparison = pd.DataFrame(data_tuples, columns=['date', 'weight_google_bm', 'weight_apple_bm', 'weight_google_rl',
                                                 'weight_apple_rl',
                                                 'tot_val_port_bm', 'tot_val_port_rl', 'diff_weight_google_bm',
                                                 'diff_weight_apple_bm', 'diff_weight_google_rl',
                                                 'diff_weight_apple_rl',
                                                 'diff_port_val_bm', 'diff_port_val_rl'])

        df_comparison = df_comparison.set_index('date')

        return df_comparison

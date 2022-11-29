import pandas as pd
from matplotlib import pyplot as plt
df = pd.read_csv(r'/Users/kiafarokhnia/Downloads/file (1).csv')




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



    weight_google_bm.append((google_pos_bm*google_hist)/(google_pos_bm*google_hist+apple_pos_bm*apple_hist+cash_bm))
    weight_apple_bm.append((apple_pos_bm*apple_hist)/(google_pos_bm*google_hist+apple_pos_bm*apple_hist+cash_bm))

    weight_google_rl.append((google_pos_rl*google_hist)/(google_pos_rl*google_hist+apple_pos_rl*apple_hist+cash_rl))
    weight_apple_rl.append((apple_pos_rl*apple_hist)/(google_pos_rl*google_hist+apple_pos_rl*apple_hist+cash_rl))

    tot_val_port_bm.append(google_pos_bm*google_hist+apple_pos_bm*apple_hist+cash_bm)
    tot_val_port_rl.append(google_pos_rl*google_hist+apple_pos_rl*apple_hist+cash_rl)

    diff_weight_google_bm.append((weight_google_bm[step]-google_weight_bm)/google_weight_bm * 100)
    diff_weight_apple_bm.append((weight_apple_bm[step]-apple_weight_bm)/apple_weight_bm * 100)

    diff_weight_google_rl.append((weight_google_rl[step]-google_weight_rl)/google_weight_rl * 100)
    diff_weight_apple_rl.append((weight_apple_rl[step]-apple_weight_rl)/apple_weight_rl * 100)

    diff_port_val_bm.append((tot_val_port_bm[step]-total_value_portfolio_bm)/total_value_portfolio_bm)
    diff_port_val_rl.append((tot_val_port_rl[step]-total_value_portfolio_rl)/total_value_portfolio_rl)



data_tuples = list(zip(df['date'], weight_google_bm, weight_apple_bm, weight_google_rl, weight_apple_rl, tot_val_port_bm,
                       tot_val_port_rl, diff_weight_google_bm, diff_weight_apple_bm, diff_weight_google_rl,
                       diff_weight_apple_rl, diff_port_val_bm, diff_port_val_rl))



new = pd.DataFrame(data_tuples, columns=['date','weight_google_bm', 'weight_apple_bm', 'weight_google_rl', 'weight_apple_rl',
                                         'tot_val_port_bm', 'tot_val_port_rl', 'diff_weight_google_bm',
                                         'diff_weight_apple_bm', 'diff_weight_google_rl', 'diff_weight_apple_rl',
                                         'diff_port_val_bm', 'diff_port_val_rl'])

new = new.set_index('date')
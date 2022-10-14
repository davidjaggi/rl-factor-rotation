#benchmark_portfolio.hist_dict['benchmark']['holdings'][-1]


hist_dict = {'benchmark':
                    {'timestamp': [], 'holdings': {'GOOGLE': [],'APPLE': []}, 'cash': []},
                'rl': {'timestamp': [], 'holdings': {'GOOGLE': [],'APPLE': []}},
                'historical_asset_prices': {'GOOGLE': [],'APPLE': []}}


dt = '2020-02-24'
date = '2020-02-25'
holding1 = [1000]
holding2 = [1000]
prices1 = [500]
prices2 = [1000]
cash = [10000]
hist_dict['benchmark']['cash'].append(cash[-1])
trx_cost = 0
hist_dict['benchmark']['timestamp'].append(dt)
hist_dict['benchmark']['holdings']['GOOGLE'].append(holding1[-1])
hist_dict['benchmark']['holdings']['APPLE'].append(holding2[-1])
hist_dict['historical_asset_prices']['GOOGLE'].append(prices1[-1])
hist_dict['historical_asset_prices']['APPLE'].append(prices2[-1])
ideal_weights = [0.5, 0.5]
delta = list()
portfolio_value = {'GOOGLE': 1 ,'APPLE': 1}



pricelist = [[1000,1000], [1100,1050], [900,1050], [950,900], [850,1200]]

for i in pricelist:
    hist_dict['historical_asset_prices']['GOOGLE'].append(i[0])
    hist_dict['historical_asset_prices']['APPLE'].append(i[1])
    portfolio_value['GOOGLE'] = hist_dict['benchmark']['holdings']['GOOGLE'][-1]*hist_dict['historical_asset_prices']['GOOGLE'][-1]
    portfolio_value['APPLE'] = hist_dict['benchmark']['holdings']['APPLE'][-1]*hist_dict['historical_asset_prices']['APPLE'][-1]


    ratio = (portfolio_value['GOOGLE']) / (portfolio_value['GOOGLE'] + portfolio_value['APPLE'])


    curr_weight = [ratio, 1 - ratio]
    ideal_weights = [0.5, 0.5]
    delta = list()

    for a, b in zip(curr_weight, ideal_weights):
        delta.append((a*-1) - (b*-1))

    delta_portfolio_value = portfolio_value['GOOGLE'] - portfolio_value['APPLE']

    if delta_portfolio_value > 0:
        nr_shares_g = delta_portfolio_value / 2 / hist_dict['historical_asset_prices']['GOOGLE'][-1]
        nr_shares_a = delta_portfolio_value / 2 / hist_dict['historical_asset_prices']['APPLE'][-1]*-1
    else:
        nr_shares_g = delta_portfolio_value / 2 / hist_dict['historical_asset_prices']['GOOGLE'][-1]*-1
        nr_shares_a = delta_portfolio_value / 2 / hist_dict['historical_asset_prices']['APPLE'][-1]


    shares_to_trade = [round(nr_shares_g, 0), round(nr_shares_a, 0)]

    # TODO: implement the ENV_CONFIG = initial_balance within this function to check if we have enough money to trade (cash within hist_dict)


    cash_google = shares_to_trade[0] * hist_dict['historical_asset_prices']['GOOGLE'][-1]
    cash_apple = shares_to_trade[1] * hist_dict['historical_asset_prices']['APPLE'][-1]

    if cash_google > 0:
        if cash_apple*-1+hist_dict['benchmark']['cash'][-1]>cash_google:
            pass
        else:
            nr_shares_g = nr_shares_g - (cash_google + cash_apple - hist_dict['benchmark']['cash'][-1])/hist_dict['historical_asset_prices']['GOOGLE'][-1]
            shares_to_trade = [round(nr_shares_g, 0), round(nr_shares_a, 0)]
            cash_google = shares_to_trade[0] * hist_dict['historical_asset_prices']['GOOGLE'][-1]

    else:
        if cash_google*-1+hist_dict['benchmark']['cash'][-1]>cash_apple:
            pass
        else:
            nr_shares_a = nr_shares_a - (cash_apple + cash_google - hist_dict['benchmark']['cash'][-1])/hist_dict['historical_asset_prices']['APPLE'][-1]
            shares_to_trade = [round(nr_shares_g, 0), round(nr_shares_a, 0)]
            cash_apple = shares_to_trade[1] * hist_dict['historical_asset_prices']['APPLE'][-1]


    cash_delta = cash_google + cash_apple


    hist_dict['benchmark']['cash'].append(hist_dict['benchmark']['cash'][-1] - cash_delta -
                                               trx_cost * (abs(shares_to_trade[0]) + abs(shares_to_trade[1])))


    hist_dict['benchmark']['timestamp'].append(date)


    new_holdings_g = hist_dict['benchmark']['holdings']['GOOGLE'][-1] + shares_to_trade[0]
    new_holdings_a = hist_dict['benchmark']['holdings']['APPLE'][-1] + shares_to_trade[1]

    hist_dict['benchmark']['holdings']['GOOGLE'].append(new_holdings_g)
    hist_dict['benchmark']['holdings']['APPLE'].append(new_holdings_a)

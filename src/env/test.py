#benchmark_portfolio.hist_dict['benchmark']['holdings'][-1]


hist_dict = {'benchmark': {'timestamp': [], 'holdings': []},
                          'rl': {'timestamp': [], 'holdings': []},
                          'historical_asset_prices': []}

dt = '2020-02-24'
holdings = [1000,1000]
prices = [1234,1567]
hist_dict['benchmark']['timestamp'].append(dt)
hist_dict['benchmark']['holdings'].append(holdings)
hist_dict['historical_asset_prices'].append(prices)
ideal_weights = [0.5,0.5]
delta = list()


class Broker():
    """ Broker class
    Args:
    """

    def __init__(self):

        self.benchmark_portfolio = None
        self.rl_portfolio = None
        self.hist_dict = {'benchmark': {'timestamp': [], 'holdings': []},
                          'rl': {'timestamp': [], 'holdings': []},
                          'historical_asset_prices': []}
        self.trade_logs = {'benchmark_portfolio': [],
                           'rl_portfolio': []}


dog=Broker()
#print(dog.hist_dict)

ratio = round(hist_dict['historical_asset_prices'][-1][0] / (hist_dict['historical_asset_prices'][-1][0] +
                                                   hist_dict['historical_asset_prices'][-1][1]),2)
curr_weight = [ratio, 1 - ratio]

ideal_weights = [0.5, 0.5]

delta = list()
for a, b in zip(curr_weight, ideal_weights):
    delta.append(round(a - b, 2))

shares_to_trade = [round(delta[0] * hist_dict['benchmark']['holdings'][-1][0],0),
                   round(delta[1] * hist_dict['benchmark']['holdings'][-1][1],0)]

print(shares_to_trade)

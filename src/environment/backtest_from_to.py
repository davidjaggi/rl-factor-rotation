# %%
import numpy as np

# %%
def backtest_from_to(weights, prices, from_date, to_date, investable):
    '''
    Backtest the performance of a portfolio form one date to another.

              Parameters:
                      weights (array): weights in percentage
                      prices (array): current prices of assets
                      balance (array): cash amount of portfolio

              Returns:
                      units (DataFrame): units to trade
                      remainder (float): cash that cannot be invested
    '''
    prices_short = prices.loc[from_date:to_date]
    units = np.floor(weights * investable / prices_short.iloc[0, :])
    cash = investable - (units * prices_short.iloc[0, :]).sum()
    stock_values = prices_short.multiply(np.array(units), axis=1)
    p_and_l = stock_values.sum(axis=1).to_frame()
    p_and_l.iloc[0, :] = investable
    return p_and_l, cash
# %%
import numpy as np
import pandas as pd


# %%
def generate_paths(spot: np.array, drift:np.array, sigma:np.array, correlation:np.matrix, start_date:str, end_date:str, dt:int):
    '''
    Simulates asset paths based on correlated geometric brownian motion.

              Parameters:
                      spot (array): starting prices
                      drift (array): daily dift parameters
                      sigma (array): daily volatilities
                      correlation (array): correlation matrix
                      start_date: Start date in format "YYYY-MM-DD"
                      end_date: End date in format "YYYY-MM-DD"
                      dt: difference between consecutive dates

              Returns:
                      df_out (DataFrame): price data which was generated
    '''

    dt_range = pd.bdate_range(start_date, end_date)
    n_sample = len(dt_range)
    nProcesses = len(spot)
    result = np.zeros(shape=(nProcesses, n_sample))

    # create one set of correlated random variates for n processes
    choleskyMatrix = np.linalg.cholesky(correlation)
    e = np.random.normal(size=(nProcesses, n_sample))
    paths = np.dot(choleskyMatrix, e)

    # generate paths
    for j in range(n_sample):
        for k in range(nProcesses):
            if (j == 0):
                result[k, j] = paths[k, j] = spot[k]
            else:
                result[k, j] = paths[k, j] = paths[k, j - 1] + drift[k] * paths[k, j - 1] * dt + sigma[k] * paths[
                    k, j - 1] * np.sqrt(dt) * paths[k, j]

    # store this in a dataframe
    data_dict = {}
    for j in range(nProcesses):
        data_dict["Asset_" + str(j)] = result[j, :]
    df_out = pd.DataFrame(data_dict, index=dt_range)
    return df_out

if __name__ == '__main__':
    # Test:
    df = generate_paths(spot=np.array([100, 100]), drift=np.array([0.05/np.sqrt(260), 0.1/np.sqrt(260)]), sigma=np.array([0.1/np.sqrt(260),0.2/np.sqrt(260)]) , correlation= np.array([[1,0.3],[0.3,1]]), start_date="2000-01-20", end_date="2001-01-20", dt=1 )
    rets = np.log(df/df.shift(1))
    print(np.sqrt(rets.var()*260))
    print(rets.corr())
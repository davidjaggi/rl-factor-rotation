# %%
import matplotlib.pyplot as plt
import numpy as np

from src.data.feed import CSVDataFeed
from src.data.rebalancing_schedule import PeriodicSchedule
from src.env.base_env import BaseEnv
from src.utils.load_path import load_data_path

# %%
data_path = load_data_path()
feed = CSVDataFeed(file_name=data_path + "/example_data.csv")

ENV_CONFIG = {
    "initial_balance": 10000,
    "initial_weights": np.array([0.5, 0.5]),
    "benchmark_type": "custom",
    "benchmark_wgts": np.array([0.5, 0.5]),
    "start_date": "2015-12-31",
    "end_date": "2020-12-31",
    "busday_offset_start": 250,
    "cost_pct": 0.0005,
    "reward_scaling": 1,
    "obs_price_hist": 5,
}

####starting here
def sharpe_ratio(rets):
    return rets.mean() / rets.std()

import numpy as np

def positions(x, theta):
    M = len(theta) - 2
    T = len(x)
    Ft = np.zeros(T)
    for t in range(M, T):
        xt = np.concatenate([[1], x[t - M:t], [Ft[t - 1]]])
        Ft[t] = np.tanh(np.dot(theta, xt))
    return Ft

def returns(Ft, x, delta):
    T = len(x)
    rets = Ft[0:T - 1] * x[1:T] - delta * np.abs(Ft[1:T] - Ft[0:T - 1])
    return np.concatenate([[0], rets])


def gradient(x, theta, delta):
    Ft = positions(x, theta)
    rets = returns(Ft, x, delta)
    T = len(x)
    M = len(theta) - 2

    A = np.mean(rets)
    B = np.mean(np.square(rets))
    S = A / np.sqrt(B - A ** 2)

    grad = np.zeros(M + 2)  # initialize gradient
    dFpdtheta = np.zeros(M + 2)  # for storing previous dFdtheta

    for t in range(M, T):
        xt = np.concatenate([[1], x[t - M:t], [Ft[t - 1]]])
        dRdF = -delta * np.sign(Ft[t] - Ft[t - 1])
        dRdFp = x[t] + delta * np.sign(Ft[t] - Ft[t - 1])
        dFdtheta = (1 - Ft[t] ** 2) * (xt + theta[-1] * dFpdtheta)
        dSdtheta = (dRdF * dFdtheta + dRdFp * dFpdtheta)
        grad = grad + dSdtheta
        dFpdtheta = dFdtheta

    return grad, S


def train(x, epochs=500, M=5, commission=0.0025, learning_rate=0.1):
    theta = np.ones(M + 2)
    sharpes = np.zeros(epochs)  # store sharpes over time
    for i in range(epochs):
        grad, sharpe = gradient(x, theta, commission)
        theta = theta + grad * learning_rate

        sharpes[i] = sharpe

    print("finished training")
    return theta, sharpes



####fin


# now try a different rebalancing frequency...
schedule = PeriodicSchedule(frequency="WOM-3FRI")
# %%
env = BaseEnv(data_feed=feed, config=ENV_CONFIG, rebalance_schedule=schedule)
obs = env.reset()
done = False
while not done:
    action = env.action_space.sample()
    # action = env.action_space.sample()
    # action = np.array([-1, 1])
    obs, rew, done, _ = env.step(action)
env.plot_current_performance()
plt.show()



# %%
env.weights_memory

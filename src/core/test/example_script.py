from DeepRL_Trading.trading_env import TradingEnvironment


if __name__ == '__main__':

    env = TradingEnvironment()
    obs = env.reset()
    done = False
    while not done:
        action = env.action_space.sample() # RL replaces this random action with sth smart
        obs, rew, done, info = env.step(action)

from src.env.base_env import BaseEnv

def create_env(config):
    # create the environment
    env = BaseEnv(config=config)
    return env

# %%
if __name__ == "__main__":
    # create the environment
    env = create_env(env_config)
    # %%
    # test the environment
    reward = test_agent(env)
    # %%
    # plot the performance of the agent
    env.plot_current_performance()
    # %%
    # plot the rewards of the agent
    env.plot_rewards()
    # %%
    # plot the actions of the agent
    env.plot_actions()

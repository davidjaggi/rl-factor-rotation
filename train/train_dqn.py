import os
import datetime
import argparse

import gym

import ray
from ray.tune.registry import register_env
from ray.rllib.agents import dqn
from ray.tune.logger import pretty_print


# this is just directories, need to see if you need it...
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


parser = argparse.ArgumentParser()

parser.add_argument("--env", type=str, default="lob_env")
parser.add_argument("--num-cpus", type=int, default=1)

parser.add_argument(
    "--framework",
    choices=["tf", "torch"],
    default="torch",
    help="The DL framework specifier.")

parser.add_argument(
    "--session_id",
    type=str,
    default="0",
    help="Session id.")

parser.add_argument(
    "--nr_episodes",
    type=int,
    default=1,
    help="Number of episodes to train.")

parser.add_argument(
    "--stop-timesteps",
    type=int,
    default=100000,
    help="Number of timesteps to train.")

parser.add_argument(
    "--stop-reward",
    type=float,
    default=0.9,
    help="Reward at which we stop training.")


def env_creator(env_config):

    """ This is a function that returns an instance of the environment we are using """

    # TODO:
    #   * insert the environment from the jupyter notebook and return it

    """
    if env_config['train_config']['train']:
        data_periods = env_config['train_config']["train_data_periods"]
    else:
        data_periods = env_config['train_config']["eval_data_periods"]

    data_start_day = datetime.datetime(year=data_periods[0], month=data_periods[1], day=data_periods[2])
    data_end_day = datetime.datetime(year=data_periods[3], month=data_periods[4], day=data_periods[5])

    lob_feed = HistoricalDataFeed(data_dir=os.path.join(DATA_DIR, "market", env_config['train_config']["symbol"]),
                                  instrument=env_config['train_config']["symbol"],
                                  start_day=data_start_day,
                                  end_day=data_end_day,
                                  samples_per_file=200)

    exclude_keys = {'train_config'}
    env_config_clean = {k: env_config[k] for k in set(list(env_config.keys())) - set(exclude_keys)}

    return TradingEnvDQN(broker=Broker(lob_feed),
                         action_space=gym.spaces.Discrete(11),
                         config=env_config_clean)
    """

    env = "OUR ENVIRONMENT IMPLEMENTATION NEEDS TO GO HERE"
    return env


if __name__ == "__main__":

    args = parser.parse_args()

    # For debugging the env or other modules, set local_mode=True
    ray.init(local_mode=True, num_cpus=args.num_cpus)
    register_env(args.env, env_creator)

    # Config necessary for RLlib training
    config = {
        "env": args.env,  # or "corridor" if registered above
        "num_workers": args.num_cpus,
        "num_envs_per_worker": 1,
        "framework": args.framework,
        "evaluation_interval": 10,
        # Number of episodes to run per evaluation period.
        "evaluation_num_episodes": 1,
        "evaluation_config": {
            "explore": False,
            "render_env": False,
        }
    }

    # config for stopping the training
    stop = {
        "training_iteration": args.nr_episodes,
        "timesteps_total": args.stop_timesteps,
        "episode_reward_mean": args.stop_reward,
    }

    dqn_config = dqn.DEFAULT_CONFIG.copy()
    dqn_config.update(config)
    trainer = dqn.DQNTrainer(config=dqn_config)

    # run manual training loop and print results after each iteration
    for _ in range(args.nr_episodes):
        result = trainer.train()
        print(pretty_print(result))
        # stop training of the target train steps or reward are reached
        if result["timesteps_total"] >= args.stop_timesteps or \
                result["episode_reward_mean"] >= args.stop_reward:
            break

    ray.shutdown()
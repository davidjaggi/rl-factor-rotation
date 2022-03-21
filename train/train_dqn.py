import os
import argparse

import numpy as np

import ray
from ray.tune.registry import register_env
from ray.rllib.agents import dqn
from ray.tune.logger import pretty_print

from src.data.rebalancing_schedule import PeriodicSchedule
from src.data.data_feed import CSVDataFeed
from src.environment.base_trading_env import TradingEnv


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


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


def env_creator(config):

    """ This is a function that returns an instance of the environment we are using """

    f_name = os.path.join(ROOT_DIR, "src/environment/example_data.csv")
    feed = CSVDataFeed(file_name=f_name)

    env_config = {"initial_balance": 10000,
                  "benchmark_type": "custom",
                  "benchmark_wgts": np.array([0.5, 0.5]),
                  "start_date": "2018-12-31",
                  "end_date": "2020-12-31",
                  "busday_offset_start": 250,
                  "cost_pct": 0.0005,
                  "reward_scaling": 1,
                  "obs_price_hist": 5}

    # now try a different rebalancing frequency...
    schedule = PeriodicSchedule(frequency='WOM-3FRI')

    env = TradingEnv(data_feed=feed, config=env_config, rebalance_schedule=schedule)
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
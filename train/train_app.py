#
#   Reinforcement Learning Optimal Trade Execution
#

import os
import time
import datetime
import argparse

import gym
import json
import numpy as np

import ray
from ray import tune
from ray.tune.registry import register_env
from ray.rllib.agents.ppo import PPOTrainer

from src.data.historical_data_feed import HistoricalDataFeed
from src.core.environment.limit_orders_setup.broker_real import Broker
from src.core.environment.limit_orders_setup.base_env_real import RewardAtStepEnv
from src.core.agent.ray_model import CustomRNNModel

from ray.rllib.models import ModelCatalog

## APPO/IMPALA
from ray.rllib.agents.impala import impala
##

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")


def init_arg_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument("--env", type=str, default="lob_env")
    parser.add_argument("--num-cpus", type=int, default=2)

    parser.add_argument(
        "--framework",
        choices=["tf", "torch"],
        default="tf",
        help="The DL framework specifier.")

    parser.add_argument(
        "--symbol",
        choices=["btc_usdt"],
        default="btcusdt",
        help="Market symbol.")

    parser.add_argument(
        "--session_id",
        type=str,
        default="0",
        help="Session id.")

    parser.add_argument(
        "--nr_episodes",
        type=int,
        default=1000000,
        help="Number of episodes to train.")

    return parser.parse_args()


def lob_env_creator(env_config):

    is_env_eval = env_config.num_workers == 0

    if is_env_eval:
        data_periods = env_config["train_config"]["eval_data_periods"]
    else:
        data_periods = env_config["train_config"]["train_data_periods"]

    data_start_day = datetime.datetime(year=data_periods[0], month=data_periods[1], day=data_periods[2])
    data_end_day = datetime.datetime(year=data_periods[3], month=data_periods[4], day=data_periods[5])

    from src.data.rebalancing_schedule import PeriodicSchedule
    from src.data.feed import CSVDataFeed
    import matplotlib.pyplot as plt

    feed = CSVDataFeed(file_name="../../data/example_data.csv")

    # now try a different rebalancing frequency...
    schedule = PeriodicSchedule(frequency="WOM-3FRI")

    env = BaseEnv(data_feed=feed, config=env_config, rebalance_schedule=schedule)
    action_space = gym.spaces.Box(low=0.0,
                                  high=1.0,
                                  shape=(1,),
                                  dtype=np.float32)

    return RewardAtStepEnv(broker=broker,
                           config=observation_space_config,
                           action_space=action_space)


def init_session_container(session_id):

    if args.session_id == "0":
        session_id = str(int(time.time()))

    session_container_path = os.path.join("data", "sessions", session_id)

    if not os.path.isdir(session_container_path):
        os.makedirs(session_container_path)

    return session_container_path


def test_agent_one_episode(config, agent_path, eval_data_periods, symbol):

    agent = PPOTrainer(config=config)
    agent.restore(agent_path)

    class DummyCfg:
        def __init__(self):
            self.num_workers = 0

        def __getitem__(self, key):

            if key == "eval_data_periods":
                return eval_data_periods

            elif key == "symbol":
                return symbol

    env = lob_env_creator(DummyCfg())

    episode_reward = 0
    done = False
    obs = env.reset()
    while not done:
        action = agent.compute_action(obs)
        obs, reward, done, info = env.step(action)
        episode_reward += reward

    return episode_reward


if __name__ == "__main__":

    args = init_arg_parser()

    # For debugging the ENV or other modules, set local_mode=True
    ray.init(num_cpus=args.num_cpus,
             local_mode=False,
             # local_mode=True,
             )

    register_env("lob_env", lob_env_creator)
    ModelCatalog.register_custom_model("end_to_end_model", CustomRNNModel)

    ## Asynchronous PPO/IMPALA
    config = impala.ImpalaTrainer.merge_trainer_configs(
        impala.DEFAULT_CONFIG,  # See keys in impala.py, which are also supported.
        {
            # Whether to use V-trace weighted advantages. If false, PPO GAE
            # advantages will be used instead.
            "vtrace": True,

            # == These two options only apply if vtrace: False ==
            # Should use a critic as a baseline (otherwise don't use value
            # baseline; required for using GAE).
            "use_critic": True,
            # If true, use the Generalized Advantage Estimator (GAE)
            # with a value function, see https://arxiv.org/pdf/1506.02438.pdf.
            "use_gae": True,
            # GAE(lambda) parameter
            "lambda": 1.0,

            # == PPO surrogate loss options ==
            "clip_param": 0.4,

            # == PPO KL Loss options ==
            "use_kl_loss": False,
            "kl_coeff": 1.0,
            "kl_target": 0.01,

            # == IMPALA optimizer params (see documentation in impala.py) ==
            "rollout_fragment_length": 50,
            "train_batch_size": 500,
            "min_iter_time_s": 10,
            "num_workers": args.num_cpus - 1,
            "num_gpus": 0,
            "num_multi_gpu_tower_stacks": 1,
            "minibatch_buffer_size": 1,
            "num_sgd_iter": 1,
            "replay_proportion": 0.0,
            "replay_buffer_num_slots": 100,
            "learner_queue_size": 16,
            "learner_queue_timeout": 300,
            "max_sample_requests_in_flight_per_worker": 2,
            "broadcast_interval": 1,
            "grad_clip": 40.0,
            "opt_type": "adam",
            "lr": 0.0005,
            "lr_schedule": None,
            # "lr_schedule": [[0, 0.01],
            #                 [3000000, 0.01]],
            "decay": 0.99,
            "momentum": 0.0,
            "epsilon": 0.1,
            "vf_loss_coeff": 0.5,
            "entropy_coeff": 0.01,
            "entropy_coeff_schedule": None,

            "env": "lob_env",
            "env_config": {"initial_balance": 10000,
                           "benchmark_type": "custom",
                           "benchmark_wgts": np.array([0.5, 0.5]),
                           "start_date": "2018-12-31",
                           "end_date": "2020-12-31",
                           "busday_offset_start": 250,
                           "cost_pct": 0.0005,
                           "reward_scaling": 1,
                           "obs_price_hist": 5,
            },
            # Eval
            "evaluation_interval": 10,
            # Number of episodes to run per evaluation period.
            "evaluation_num_episodes": 1,
            "evaluation_config": {
                "explore": False,
                "render_env": True,
            },
            "model": {
                "custom_model": "end_to_end_model",
                "custom_model_config": {"fcn_depth": 128,
                                        "lstm_cells": 256},
            },
            "log_level": "WARN",
        },
        _allow_unknown_configs=True,
    )

    ##
    session_container_path = init_session_container(args.session_id)
    # with open(os.path.join(session_container_path, "config.json"), "a", encoding="utf-8") as f:
    #     json.dump(config, f, ensure_ascii=False, indent=4)

    # PPOTrainer
    experiment = tune.run("APPO",
                          config=config,
                          metric="episode_reward_mean",
                          mode="max",
                          checkpoint_freq=10,
                          stop={"training_iteration": args.nr_episodes},
                          checkpoint_at_end=True,
                          local_dir=session_container_path,
                          max_failures=-1
                          )

    # checkpoints = experiment.get_trial_checkpoints_paths(trial=experiment.get_best_trial("episode_reward_mean"),
    #                                                      metric="episode_reward_mean")
    # checkpoint_path = checkpoints[0][0]
    #
    # reward = test_agent_one_episode(config=config,
    #                                 agent_path=checkpoint_path,
    #                                 eval_data_periods=[2021, 6, 21, 2021, 6, 21],
    #                                 symbol="btcusdt")
    # print(reward)

    ray.shutdown()

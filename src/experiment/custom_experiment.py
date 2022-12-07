import numpy as np
import ray
import ray.tune as tune

from src.env.create_env import create_env


class CustomExperiment():
    def __init__(self, config, env, agent, save_dir):
        ray.shutdown()
        ray.init()
        self.config = config
        self.env = env
        self.agent = agent
        self.save_dir = save_dir

    def train(self, stop_criteria):
        """
        Train an RLlib PPO agent using tune until any of the configured stopping criteria is met.
        :param stop_criteria: Dict with stopping criteria.
            See https://docs.ray.io/en/latest/tune/api_docs/execution.html#tune-run
        :return: Return the path to the saved agent (checkpoint) and tune's ExperimentAnalysis object
            See https://docs.ray.io/en/latest/tune/api_docs/analysis.html#experimentanalysis-tune-experimentanalysis
        """
        analysis = ray.tune.run(self.agent, config=self.config, local_dir=self.save_dir, stop=stop_criteria,
                                checkpoint_at_end=True)
        # list of lists: one list per checkpoint; each checkpoint list contains 1st the path, 2nd the metric value
        checkpoints = analysis.get_trial_checkpoints_paths(trial=analysis.get_best_trial('episode_reward_mean'),
                                                           metric='episode_reward_mean')
        # retriev the checkpoint path; we only have a single checkpoint, so take the first one
        checkpoint_path = checkpoints[0][0]
        return checkpoint_path, analysis

    def load(self, path):
        """
        Load a trained RLlib agent from the specified path. Call this before testing a trained agent.
        :param path: Path pointing to the agent's saved checkpoint (only used for RLlib agents)
        """
        self.agent = self.agent(config=self.config)
        self.agent.restore(path)

    def test(self):
        env = create_env(self.config["env_config"])
        episode_reward = np.array([0])
        done = False
        obs = env.reset()
        while not done:
            action = self.agent.compute_single_action(obs)
            obs, rew, done, _ = env.step(action)
            episode_reward = np.append(episode_reward, rew)
        return episode_reward

    def register_env(self, env_name, env_creator):
        """
        Register an environment with the experiment.
        :param env_name: Name of the environment
        :param env_creator: Function that creates the environment
        """
        # register the environment with the experiment
        tune.register_env(env_name, env_creator)

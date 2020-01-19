import os
from typing import Tuple, List

from ray.rllib.env import ExternalEnv
from ray.rllib.env.external_env import _ExternalEnvEpisode

from approaches.reinforced.action_state_processor import ActionStateProcessor
from approaches.reinforced.constants import INVALID_ACTION, INVALID_ACTION_PENALTY
from approaches.reinforced.observation_state_processor import ObservationStateProcessor
from models import actions
from models.actions import Action
from models.gamestate import GameState

SERVER_ADDRESS = "localhost"
SERVER_PORT = int(os.getenv('SERVER_PORT', '50123'))
CHECKPOINT_FILE = "last_checkpoint.out"


class InferenceIC20Environment(ExternalEnv):

    def __init__(self, obs_space_processor: ObservationStateProcessor,
                 act_space_processor: ActionStateProcessor, trial_max: int = 0):
        self.trial_max = trial_max
        self.obs_space_processor = obs_space_processor
        self.act_space_processor = act_space_processor

        action_space = act_space_processor.generate_action_space()
        obs_space = obs_space_processor.generate_observation_space()

        ExternalEnv.__init__(self, action_space=action_space,
                             observation_space=obs_space)

    def run(self):
        print("Do not start policy server because inference.")

    def get_action(self, episode_id, observation: GameState) -> Tuple[Action, float]:
        """Record an obs and get the on-policy action.

                Arguments:
                    episode_id (str): Episode id returned from start_episode().
                    observation (obj): Current environment obs.

                Returns:
                    action (obj): Action from the env action space.
                """

        episode = self._get(episode_id)
        action, penalty = self._choose_actionable_action(episode, observation)
        return action, penalty

    def end_episode(self, episode_id, observation):
        """Record the end of an episode.

        Arguments:
            episode_id (str): Episode id returned from start_episode().
            observation (obj): Current environment obs.
        """

        preprocessed_observation = self.obs_space_processor.preprocess_obs(observation)

        episode = self._get(episode_id)
        self._finished.add(episode.episode_id)
        episode.done(preprocessed_observation)

    def _choose_actionable_action(self, episode, observation) -> Tuple[Action, float]:
        preprocessed_observation = self.obs_space_processor.preprocess_obs(observation)
        mapped_action = INVALID_ACTION
        penalty = 0

        trial_count = 0
        while (mapped_action == INVALID_ACTION or mapped_action.cost > observation.points) \
                or mapped_action not in actions.generate_possible_actions(observation):
            action = self._wait_for_action(preprocessed_observation, episode)
            mapped_action, penalty = self.act_space_processor.map_action(action, observation)

            trial_count += 1
            if trial_count >= self.trial_max:
                mapped_action = INVALID_ACTION
                penalty = INVALID_ACTION_PENALTY
                break

        return mapped_action, penalty

    # noinspection PyProtectedMember
    @classmethod
    def _wait_for_action(cls, observation: List, episode: _ExternalEnvEpisode):
        """
        Dark magic. Workaround for the _Episode.wait_for_action method
        :param observation:
        :param episode:
        :return:
        """
        if episode.multiagent:
            episode.new_observation_dict = observation
        else:
            episode.new_observation = observation
        episode._send()
        return episode.action_queue.get(True)

    def log_returns(self, episode_id, reward, info=None):
        episode = self._get(episode_id)
        episode.cur_reward += reward
        print(f"Episode Reward: {episode.cur_reward}")
        if info:
            episode.cur_info = info or {}

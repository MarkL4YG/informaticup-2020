import os
import socket
from typing import Tuple, List

import numpy as np
from gym import spaces
from gym.spaces import Box, Discrete
from ray.rllib.env import ExternalEnv

from approaches.reinforced.constants import MAX_CITIES, MAX_ACTIONSPACE, CITY_ACTIONSPACE, \
    MAX_PATHOGENS, NEUTRAL_REWARD, MAX_CONNECTIONS, GLOBAL_ACTIONSPACE, INVALID_ACTION
from approaches.reinforced.observation_preprocessors import NaivePreprocessor
from approaches.reinforced.policy_server import MyServer
from approaches.reinforced.util import timer
from models import actions
from models.actions import Action
from models.gamestate import GameState
from models.pathogen import Pathogen

SERVER_ADDRESS = "localhost"
SERVER_PORT = int(os.getenv('SERVER_PORT', '50123'))
CHECKPOINT_FILE = "last_checkpoint.out"
UINT32_MAX = np.iinfo(np.uint32).max


class SimplifiedIC20Environment(ExternalEnv):
    """
    # Todo: Make this a Multi-Agent ExternalEnv
    """

    def __init__(self):
        action_space = self._get_simple_action_space_all_cities()

        single_city_obs = self._get_observation_space_single_city()
        obs_space = self.aggregate_space_over_cities(single_city_obs)
        self.preprocessor = NaivePreprocessor()

        ExternalEnv.__init__(self, action_space=action_space,
                             observation_space=spaces.Tuple(obs_space),
                             max_concurrent=2)

    def aggregate_space_over_cities(self, action_space: spaces.Space):
        aggregated_space = []
        for _ in range(MAX_CITIES):
            aggregated_space.append(action_space)
        return aggregated_space

    def _get_simple_action_space_all_cities(self):
        return spaces.Discrete(MAX_ACTIONSPACE)

    def _get_observation_space_single_city(self):
        # latitude, longitude
        location = spaces.Tuple((Box(low=-90, high=90, shape=(1,), dtype=np.float32),
                                 Box(low=-180, high=180, shape=(1,), dtype=np.float32)))
        # population
        population = Box(low=0, high=UINT32_MAX, shape=(1,), dtype=np.uint32)
        # connections
        connections = Discrete(MAX_CONNECTIONS + 1)  # -> represents [0, MAX_CONNECTIONS]
        # economyStrength, governmentStability, hygieneStandards, populationAwareness
        attributes = Box(low=-2, high=2, shape=(4,), dtype=np.int8)
        # city_pathogens
        pathogens = self._build_multi_space(self._pathogen_representation(), 5)
        # events have been left out yet, todo: handle them when the time is right.
        return spaces.Tuple((location, population, connections, attributes, pathogens))

    def get_available_port(self, address: str) -> int:
        s = socket.socket()
        s.bind((address, 0))
        available_port = s.getsockname()[1]
        s.close()
        return available_port

    def run(self):
        available_port = self.get_available_port(SERVER_ADDRESS)
        print("Starting policy server at {}:{}".format(SERVER_ADDRESS,
                                                       available_port))
        server = MyServer(self, SERVER_ADDRESS, available_port, self.preprocessor)
        server.serve_forever()

    def _build_multidiscrete(self, nvec: list):
        space = []
        for val in nvec:
            space.append(Discrete(val))
        return spaces.Tuple(space)

    def _build_multibinary(self, n: int):
        return self._build_multi_space(Discrete(2), n)

    def _build_multi_space(self, duplicated_space, n: int):
        space = []
        for _ in range(n):
            space.append(duplicated_space)
        return spaces.Tuple(space)

    def _pathogen_representation(self):
        return spaces.Tuple((
            Discrete(9),  # see _map_pathogen_status
            Box(low=0, high=UINT32_MAX, shape=(1,), dtype=np.uint32),  # infected-population
            Box(low=-2, high=2, shape=(4,), dtype=np.int8)  # infectivity, mobility, duration, lethality
        ))

    def get_action(self, episode_id, observation) -> Tuple[str, dict, float]:
        """Record an observation and get the on-policy action.

                Arguments:
                    episode_id (str): Episode id returned from start_episode().
                    observation (obj): Current environment observation.

                Returns:
                    action (obj): Action from the env action space.
                """

        episode = self._get(episode_id)
        preprocessed_observation = self.preprocessor.preprocess(observation)[:MAX_CITIES]
        action, penalty = self._choose_affordable_action(episode, preprocessed_observation, observation)
        action_json = action.json
        print(f"Action: {action_json}")
        return action_json, preprocessed_observation, penalty

    def _choose_affordable_action(self, episode, preprocessed_observation, observation) -> Tuple[Action, float]:
        action = self.wait_for_action(preprocessed_observation, episode)
        print(f'discrete-action: {action}')
        mapped_action, penalty = self._map_actions(action, observation)
        while mapped_action.cost > observation.points:
            action = self.wait_for_action(preprocessed_observation, episode)
            mapped_action, penalty = self._map_actions(action, observation)
        return mapped_action, penalty

    def wait_for_action(self, observation, episode):
        """
        Dark magic. Workaround for topthe _Episode.wait_for_action method
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

    def _map_actions(self, chosen_action, state: GameState) -> Tuple[Action, float]:
        if chosen_action < GLOBAL_ACTIONSPACE:
            return self._map_global_actions(chosen_action, state)
        else:
            return self._map_city_actions(chosen_action - GLOBAL_ACTIONSPACE, state)

    def _map_global_actions(self, chosen_action, game_state: GameState) -> Tuple[Action, float]:
        options = {
            0: actions.end_round(),
        }
        basic_options_len = len(options)
        if chosen_action < basic_options_len:
            mapped_action = options.get(chosen_action)
        else:
            available_pathogens = self.preprocessor.sort_pathogens(game_state.pathogens,
                                                                   game_state.cities)[:MAX_PATHOGENS]
            pathogens_with_vaccine = [*game_state.pathogens_with_vaccination,
                                      *game_state.pathogens_with_vaccination_in_development]
            pathogens_with_meds = [*game_state.pathogens_with_medication,
                                   *game_state.pathogens_with_medication_in_development]

            available_pathogens_without_vaccine = list(filter(lambda pathogen: pathogen not in pathogens_with_vaccine,
                                                              available_pathogens))
            available_pathogens_without_medication = list(filter(lambda pathogen: pathogen not in pathogens_with_meds,
                                                                 available_pathogens))

            vaccine_actions = {i: action for i, action in enumerate(
                self.generate_global_vaccine_actions(available_pathogens, available_pathogens_without_vaccine),
                start=basic_options_len)}

            medication_actions = {i: action for i, action in enumerate(
                self.generate_global_med_actions(available_pathogens, available_pathogens_without_medication),
                start=basic_options_len + MAX_PATHOGENS)}

            options.update(vaccine_actions)
            options.update(medication_actions)
            mapped_action = options.get(chosen_action)

        return self.penalize_action(mapped_action, game_state)

    def _map_city_actions(self, chosen_action, game_state: GameState) -> Tuple[Action, float]:
        city_id = int(np.floor(chosen_action / CITY_ACTIONSPACE))
        action = chosen_action % CITY_ACTIONSPACE
        city = game_state.cities[city_id]

        options = {0: actions.quarantine_city(city_id, number_of_rounds=2),
                   1: actions.close_airport(city_id, number_of_rounds=2),
                   2: actions.apply_hygienic_measures(city_id),
                   3: actions.exert_political_influence(city_id),
                   4: actions.call_for_elections(city_id),
                   6: actions.launch_campaign(city_id)}
        basic_options_len = len(options)

        if action < basic_options_len:
            mapped_action = options.get(action)
        else:
            available_pathogens = self.preprocessor.sort_pathogens(game_state.pathogens,
                                                                   game_state.cities)[:MAX_PATHOGENS]

            vaccine_actions = {i: action for i, action in enumerate(
                self.generate_city_vaccine_actions(city, available_pathogens,
                                                   game_state.pathogens_with_vaccination),
                start=basic_options_len)}

            medication_actions = {i: action for i, action in enumerate(
                self.generate_city_med_actions(city, available_pathogens, game_state.pathogens_with_medication),
                start=basic_options_len + MAX_PATHOGENS)}

            options.update(vaccine_actions)
            options.update(medication_actions)
            mapped_action = options.get(action)

        return self.penalize_action(mapped_action, game_state)

    def penalize_action(self, action: Action, game_state: GameState):
        if action in actions.generate_possible_actions_parallelized(game_state):
            if action == INVALID_ACTION:
                penalty = -20
                return actions.end_round(), penalty
            else:
                return action, NEUTRAL_REWARD
        else:
            penalty = -20
            return actions.end_round(), penalty

    def generate_city_vaccine_actions(self, city, ordered_available_pathogens: List[Pathogen],
                                      pathogens_with_vaccination: List[Pathogen]):
        city_pathogens_with_vaccine = filter(lambda city_pathogen:
                                             city_pathogen in pathogens_with_vaccination,
                                             city.pathogens)
        ordered_city_pathogens_with_vaccine = [actions.deploy_vaccine(pathogen.index, city.index)
                                               if pathogen in city_pathogens_with_vaccine
                                               else INVALID_ACTION
                                               for pathogen in ordered_available_pathogens]
        return ordered_city_pathogens_with_vaccine

    def generate_city_med_actions(self, city, ordered_available_pathogens: List[Pathogen],
                                  pathogens_with_medication: List[Pathogen]):
        city_pathogens_with_medication = filter(lambda city_pathogen:
                                                city_pathogen in pathogens_with_medication,
                                                city.pathogens)
        ordered_city_pathogens_with_medication = [actions.deploy_vaccine(pathogen.index, city.index)
                                                  if pathogen in city_pathogens_with_medication
                                                  else INVALID_ACTION
                                                  for pathogen in ordered_available_pathogens]
        return ordered_city_pathogens_with_medication

    def generate_global_vaccine_actions(self, gamestate_pathogens: List[Pathogen],
                                        pathogens_without_vaccination: List[Pathogen]):

        ordered_gamestate_pathogens_with_vaccine = map(lambda gamestate_pathogen:
                                                          actions.develop_vaccine(gamestate_pathogen.index)
                                                          if gamestate_pathogen in pathogens_without_vaccination
                                                          else INVALID_ACTION,
                                                          gamestate_pathogens)
        return ordered_gamestate_pathogens_with_vaccine

    def generate_global_med_actions(self, gamestate_pathogens: List[Pathogen],
                                    pathogens_without_medication: List[Pathogen]):

        ordered_gamestate_pathogens_with_medication = map(lambda gamestate_pathogen:
                                                          actions.develop_medication(gamestate_pathogen.index)
                                                          if gamestate_pathogen in pathogens_without_medication
                                                          else INVALID_ACTION,
                                                          gamestate_pathogens)
        return ordered_gamestate_pathogens_with_medication

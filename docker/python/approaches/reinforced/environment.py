import os
import socket
from typing import Tuple

import numpy as np
from gym import spaces
from gym.spaces import Box, Discrete
from ray.rllib.env import ExternalEnv

from approaches.reinforced.constants import MAX_CITIES, MAX_ACTIONSPACE, END_ROUND_ACTION, BASE_ACTIONSPACE, \
    MAX_PATHOGENS, NEUTRAL_REWARD, MAX_CONNECTIONS
from approaches.reinforced.observation_preprocessors import naive_city_state_preprocessing
from approaches.reinforced.policy_server import MyServer
from models import actions
from models.actions import Action
from models.gamestate import GameState

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

        ExternalEnv.__init__(self, action_space=action_space,
                             observation_space=spaces.Tuple(obs_space),
                             max_concurrent=2)

    def aggregate_space_over_cities(self, action_space: spaces.Space):
        aggregated_space = []
        for _ in range(MAX_CITIES):
            aggregated_space.append(action_space)
        return aggregated_space

    def _get_simple_action_space_all_cities(self):
        # do_nothing[1], [quarantine[2], close-airport[3], hygienic_measures [4], political-influence[5],
        # call-for-elections[6], launch-campaign [7],
        # vaccine[8], vaccine2[9], vaccine3[10], vaccine4[11], vaccine5[12],
        # med1[13], med2[14], med3[15], med4[16], med5[17]]
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
        # pathogens
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
        server = MyServer(self, SERVER_ADDRESS, available_port)
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
            Discrete(2),  # is_active
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
        preprocessed_city_states = naive_city_state_preprocessing(observation)[:MAX_CITIES]
        city_action = self.wait_for_action(preprocessed_city_states, episode)
        mapped_city_action, penalty = self._map_city_actions(city_action, observation)
        while mapped_city_action.get_cost() > observation.get_available_points():
            city_action = self.wait_for_action(preprocessed_city_states, episode)
            mapped_city_action, penalty = self._map_city_actions(city_action, observation)
        action_json = mapped_city_action.get_json()
        print(f"Action: {action_json}")
        return action_json, preprocessed_city_states, penalty

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

    def _map_city_actions(self, chosen_action, state: GameState) -> Tuple[Action, float]:
        if chosen_action == END_ROUND_ACTION:
            return actions.end_round(), NEUTRAL_REWARD
        else:
            city_action = chosen_action - 1
            city_id = city_action % BASE_ACTIONSPACE
            action = int(np.ceil(city_action / BASE_ACTIONSPACE))
            city = state.get_cities()[city_id]
            options = {
                0: actions.quarantine_city(city_id, number_of_rounds=2),
                1: actions.close_airport(city_id, number_of_rounds=2),
                2: actions.apply_hygienic_measures(city_id),
                3: actions.exert_political_influence(city_id),
                4: actions.call_for_elections(city_id),
                6: actions.launch_campaign(city_id)
            }
            basic_options_len = len(options)
            city_pathogens_with_vaccine = filter(lambda city_vaccine:
                                                 city_vaccine in state.get_pathogens_with_vaccination(),
                                                 city.get_pathogens())
            vaccine_actions = {i: actions.deploy_vaccine(pathogen.get_id(), city_id)
                               for i, pathogen in enumerate(city_pathogens_with_vaccine,
                                                            start=basic_options_len)}

            city_pathogens_with_medication = filter(lambda city_vaccine:
                                                    city_vaccine in state.get_pathogens_with_medication(),
                                                    city.get_pathogens())
            medication_actions = {i: actions.deploy_vaccine(pathogen.get_id(), city_id)
                                  for i, pathogen in enumerate(city_pathogens_with_medication,
                                                               start=basic_options_len + MAX_PATHOGENS)}
            options.update(vaccine_actions)
            options.update(medication_actions)
            action = options.get(action)
            if action in actions.generate_possible_actions_parallelized(state):
                return action, NEUTRAL_REWARD
            else:
                penalty = -20
                return actions.end_round(), penalty

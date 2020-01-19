import abc
from typing import List, Tuple, Callable, Optional

import numpy as np
from gym import Space, spaces

from approaches.reinforced.constants import MAX_ACTIONSPACE, MAX_PATHOGENS, CITY_ACTIONSPACE, INVALID_ACTION, \
    GLOBAL_ACTIONSPACE, NEUTRAL_REWARD, INVALID_ACTION_PENALTY, MAX_CITY_ACTIONSPACE
from models import actions
from models.actions import Action
from models.city import City
from models.gamestate import GameState
from models.pathogen import Pathogen


class ActionStateProcessor(abc.ABC):
    def __init__(self, sort_pathogens: Callable[[List[Pathogen], GameState], List[Pathogen]]):
        self.sort_pathogens = sort_pathogens

    @abc.abstractmethod
    def generate_action_space(self) -> Space:
        pass

    @abc.abstractmethod
    def map_action(self, chosen_action: int, game_state: GameState) -> Tuple[Optional[Action], float]:
        pass


class SimpleActStateProcessor(ActionStateProcessor):

    def __init__(self, sort_pathogens: Callable[[List[Pathogen], GameState], List[Pathogen]]):
        super().__init__(sort_pathogens)

    def generate_action_space(self) -> Space:
        return spaces.Discrete(MAX_ACTIONSPACE)

    def map_action(self, chosen_action: int, game_state: GameState) -> Tuple[Optional[Action], float]:
        if chosen_action < GLOBAL_ACTIONSPACE:
            mapped_action = self._map_global_actions(chosen_action, game_state)
        else:
            mapped_action = self._map_city_actions(chosen_action - GLOBAL_ACTIONSPACE, game_state)

        return self.penalize_action(mapped_action, game_state)

    def _map_global_actions(self, chosen_action: int, game_state: GameState) -> Optional[Action]:
        assert chosen_action < GLOBAL_ACTIONSPACE
        options = {
            0: actions.end_round()
        }
        basic_options_len = len(options)
        if chosen_action < basic_options_len:
            mapped_action = options.get(chosen_action)
        else:
            ordered_available_pathogens = self.sort_pathogens(game_state.pathogens, game_state)
            pathogens_with_vaccine = [*game_state.pathogens_with_vaccination,
                                      *game_state.pathogens_with_vaccination_in_development]
            pathogens_with_meds = [*game_state.pathogens_with_medication,
                                   *game_state.pathogens_with_medication_in_development]

            vaccine_actions = {i: action for i, action in enumerate(
                self._generate_global_vaccine_actions(ordered_available_pathogens, pathogens_with_vaccine),
                start=basic_options_len)}

            medication_actions = {i: action for i, action in enumerate(
                self._generate_global_med_actions(ordered_available_pathogens, pathogens_with_meds),
                start=basic_options_len + MAX_PATHOGENS)}

            options.update(vaccine_actions)
            options.update(medication_actions)
            mapped_action = options.get(chosen_action)

        return mapped_action

    def _map_city_actions(self, chosen_action, game_state: GameState) -> Optional[Action]:
        assert chosen_action < MAX_CITY_ACTIONSPACE
        action_id, city_id = self._transform_for_city_action(chosen_action)
        city = game_state.cities[city_id]

        options = {0: actions.quarantine_city(city_id, number_of_rounds=2),
                   1: actions.close_airport(city_id, number_of_rounds=2),
                   2: actions.apply_hygienic_measures(city_id),
                   3: actions.exert_political_influence(city_id),
                   4: actions.call_for_elections(city_id),
                   5: actions.launch_campaign(city_id)}
        basic_options_len = len(options)

        if action_id < basic_options_len:
            mapped_action = options.get(action_id)
        else:
            ordered_available_pathogens = self.sort_pathogens(game_state.pathogens, game_state)

            vaccine_actions = {i: action for i, action in enumerate(
                self._generate_city_vaccine_actions(city, ordered_available_pathogens,
                                                    game_state.pathogens_with_vaccination),
                start=basic_options_len)}

            medication_actions = {i: action for i, action in enumerate(
                self._generate_city_med_actions(city, ordered_available_pathogens,
                                                game_state.pathogens_with_medication),
                start=basic_options_len + MAX_PATHOGENS)}

            options.update(vaccine_actions)
            options.update(medication_actions)
            mapped_action = options.get(action_id)

        return mapped_action

    @classmethod
    def _transform_for_city_action(cls, chosen_action: int) -> Tuple[int, int]:
        city_id = int(np.floor(chosen_action / CITY_ACTIONSPACE))
        action_id = chosen_action % CITY_ACTIONSPACE
        return action_id, city_id

    @classmethod
    def _generate_city_vaccine_actions(cls, city: City, ordered_available_pathogens: List[Pathogen],
                                       pathogens_with_vaccination: List[Pathogen]):
        city_pathogens_with_vaccine = list(filter(lambda city_pathogen:
                                                  city_pathogen in pathogens_with_vaccination,
                                                  city.pathogens))

        ordered_city_pathogens_with_vaccine = [actions.deploy_vaccine(pathogen.index, city.index)
                                               if pathogen in city_pathogens_with_vaccine
                                               else INVALID_ACTION
                                               for pathogen in ordered_available_pathogens]
        return ordered_city_pathogens_with_vaccine

    @classmethod
    def _generate_city_med_actions(cls, city: City, ordered_available_pathogens: List[Pathogen],
                                   pathogens_with_medication: List[Pathogen]):
        city_pathogens_with_medication = list(filter(lambda city_pathogen:
                                                     city_pathogen in pathogens_with_medication,
                                                     city.pathogens))
        ordered_city_pathogens_with_medication = [actions.deploy_medication(pathogen.index, city.index)
                                                  if pathogen in city_pathogens_with_medication
                                                  else INVALID_ACTION
                                                  for pathogen in ordered_available_pathogens]
        return ordered_city_pathogens_with_medication

    @classmethod
    def _generate_global_vaccine_actions(cls, ordered_available_pathogens: List[Pathogen],
                                         pathogens_with_vaccination: List[Pathogen]):

        ordered_gamestate_pathogens_with_vaccine = map(lambda gamestate_pathogen:
                                                       actions.develop_vaccine(gamestate_pathogen.index)
                                                       if gamestate_pathogen not in pathogens_with_vaccination
                                                       else INVALID_ACTION,
                                                       ordered_available_pathogens)
        return ordered_gamestate_pathogens_with_vaccine

    @classmethod
    def _generate_global_med_actions(cls, ordered_available_pathogens: List[Pathogen],
                                     pathogens_with_medication: List[Pathogen]):

        ordered_gamestate_pathogens_with_medication = map(lambda gamestate_pathogen:
                                                          actions.develop_medication(gamestate_pathogen.index)
                                                          if gamestate_pathogen not in pathogens_with_medication
                                                          else INVALID_ACTION,
                                                          ordered_available_pathogens)
        return ordered_gamestate_pathogens_with_medication

    @classmethod
    def penalize_action(cls, action: Action, game_state: GameState) -> Tuple[Optional[Action], float]:
        if action in actions.generate_possible_actions(game_state):
            if action == INVALID_ACTION:
                penalty = INVALID_ACTION_PENALTY
                return action, penalty
            else:
                return action, NEUTRAL_REWARD
        else:
            penalty = INVALID_ACTION_PENALTY
            return action, penalty

import abc
from typing import List, Tuple, Callable, Optional

import numpy as np
from gym import Space, spaces

from approaches.reinforced.constants import MAX_ACTIONSPACE, MAX_PATHOGENS, CITY_ACTIONSPACE, INVALID_ACTION, \
    GLOBAL_ACTIONSPACE, NEUTRAL_REWARD
from models import actions
from models.actions import Action
from models.gamestate import GameState
from models.pathogen import Pathogen


class ActionStateProcessor(abc.ABC):
    def __init__(self, sort_pathogens: Callable[..., List[Pathogen]]):
        self.sort_pathogens = sort_pathogens

    @abc.abstractmethod
    def generate_action_space(self) -> Space:
        pass

    @abc.abstractmethod
    def map_action(self, chosen_action: int, game_state: GameState) -> Tuple[Optional[Action], float]:
        pass


class SimpleActStateProcessor(ActionStateProcessor):

    def __init__(self, sort_pathogens: Callable[..., List[Pathogen]]):
        super().__init__(sort_pathogens)

    def generate_action_space(self) -> Space:
        return spaces.Discrete(MAX_ACTIONSPACE)

    def map_action(self, chosen_action: int, game_state: GameState) -> Tuple[Optional[Action], float]:
        if chosen_action < GLOBAL_ACTIONSPACE:
            mapped_action = self._map_global_actions(chosen_action, game_state)
        else:
            mapped_action = self._map_city_actions(chosen_action - GLOBAL_ACTIONSPACE, game_state)

        return self.penalize_action(mapped_action, game_state)

    def _map_global_actions(self, chosen_action, game_state: GameState) -> Optional[Action]:
        options = {
            0: actions.end_round(),
        }
        basic_options_len = len(options)
        if chosen_action < basic_options_len:
            mapped_action = options.get(chosen_action)
        else:
            available_pathogens = self.sort_pathogens(game_state.get_pathogens(),
                                                      game_state.get_cities())
            pathogens_with_vaccine = [*game_state.get_pathogens_with_vaccination(),
                                      *game_state.get_pathogens_with_vaccination_in_development()]
            pathogens_with_meds = [*game_state.get_pathogens_with_medication(),
                                   *game_state.get_pathogens_with_medication_in_development()]

            available_pathogens_without_vaccine = list(filter(lambda pathogen: pathogen not in pathogens_with_vaccine,
                                                              available_pathogens))
            available_pathogens_without_medication = list(filter(lambda pathogen: pathogen not in pathogens_with_meds,
                                                                 available_pathogens))

            vaccine_actions = {i: action for i, action in enumerate(
                self._generate_global_vaccine_actions(available_pathogens, available_pathogens_without_vaccine),
                start=basic_options_len)}

            medication_actions = {i: action for i, action in enumerate(
                self._generate_global_med_actions(available_pathogens, available_pathogens_without_medication),
                start=basic_options_len + MAX_PATHOGENS)}

            options.update(vaccine_actions)
            options.update(medication_actions)
            mapped_action = options.get(chosen_action)

        return mapped_action

    def _map_city_actions(self, chosen_action, game_state: GameState) -> Optional[Action]:
        city_id = int(np.floor(chosen_action / CITY_ACTIONSPACE))
        action = chosen_action % CITY_ACTIONSPACE
        city = game_state.get_cities()[city_id]

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
            available_pathogens = self.sort_pathogens(game_state.get_pathogens(),
                                                      game_state.get_cities())

            vaccine_actions = {i: action for i, action in enumerate(
                self._generate_city_vaccine_actions(city, available_pathogens,
                                                    game_state.get_pathogens_with_vaccination()),
                start=basic_options_len)}

            medication_actions = {i: action for i, action in enumerate(
                self._generate_city_med_actions(city, available_pathogens, game_state.get_pathogens_with_medication()),
                start=basic_options_len + MAX_PATHOGENS)}

            options.update(vaccine_actions)
            options.update(medication_actions)
            mapped_action = options.get(action)

        return mapped_action

    @classmethod
    def _generate_city_vaccine_actions(cls, city, ordered_available_pathogens: List[Pathogen],
                                       pathogens_with_vaccination: List[Pathogen]):
        city_pathogens_with_vaccine = filter(lambda city_pathogen:
                                             city_pathogen in pathogens_with_vaccination,
                                             city.get_pathogens())
        ordered_city_pathogens_with_vaccine = [actions.deploy_vaccine(pathogen.get_id(), city.get_city_id())
                                               if pathogen in city_pathogens_with_vaccine
                                               else INVALID_ACTION
                                               for pathogen in ordered_available_pathogens]
        return ordered_city_pathogens_with_vaccine

    @classmethod
    def _generate_city_med_actions(cls, city, ordered_available_pathogens: List[Pathogen],
                                   pathogens_with_medication: List[Pathogen]):
        city_pathogens_with_medication = filter(lambda city_pathogen:
                                                city_pathogen in pathogens_with_medication,
                                                city.get_pathogens())
        ordered_city_pathogens_with_medication = [actions.deploy_vaccine(pathogen.get_id(), city.get_city_id())
                                                  if pathogen in city_pathogens_with_medication
                                                  else INVALID_ACTION
                                                  for pathogen in ordered_available_pathogens]
        return ordered_city_pathogens_with_medication

    @classmethod
    def _generate_global_vaccine_actions(cls, gamestate_pathogens: List[Pathogen],
                                         pathogens_without_vaccination: List[Pathogen]):

        ordered_gamestate_pathogens_with_vaccine = map(lambda gamestate_pathogen:
                                                       actions.develop_vaccine(gamestate_pathogen.get_id())
                                                       if gamestate_pathogen in pathogens_without_vaccination
                                                       else INVALID_ACTION,
                                                       gamestate_pathogens)
        return ordered_gamestate_pathogens_with_vaccine

    @classmethod
    def _generate_global_med_actions(cls, gamestate_pathogens: List[Pathogen],
                                     pathogens_without_medication: List[Pathogen]):

        ordered_gamestate_pathogens_with_medication = map(lambda gamestate_pathogen:
                                                          actions.develop_medication(gamestate_pathogen.get_id())
                                                          if gamestate_pathogen in pathogens_without_medication
                                                          else INVALID_ACTION,
                                                          gamestate_pathogens)
        return ordered_gamestate_pathogens_with_medication

    @classmethod
    def penalize_action(cls, action: Action, game_state: GameState) -> Tuple[Optional[Action], float]:
        if action in actions.generate_possible_actions_parallelized(game_state):
            if action == INVALID_ACTION:
                penalty = -1
                return action, penalty
            else:
                return action, NEUTRAL_REWARD
        else:
            penalty = -1
            return action, penalty

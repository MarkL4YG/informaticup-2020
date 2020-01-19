import abc
from functools import reduce
from itertools import repeat
from typing import List, Callable, Tuple

import numpy as np
from gym import spaces
from gym.spaces import Space, Box, Discrete

from approaches.reinforced.constants import MAX_CITIES, MAX_CONNECTIONS, MAX_PATHOGENS, UINT32_MAX
from approaches.reinforced.util import build_multi_space
from models.city import City
from models.gamestate import GameState
from models.pathogen import Pathogen


class ObservationStateProcessor(abc.ABC):

    def __init__(self, pathogen_sorting_strategy: Callable[..., float]):
        self.pathogen_sorting_strategy = pathogen_sorting_strategy

    @abc.abstractmethod
    def generate_observation_space(self) -> Space:
        pass

    @abc.abstractmethod
    def preprocess_obs(self, game_state: GameState) -> List:
        pass

    @abc.abstractmethod
    def sort_pathogens(self, *args, **kwargs) -> List[Pathogen]:
        pass


class SimpleObsStateProcessor(ObservationStateProcessor):

    def __init__(self, pathogen_sorting_strategy: Callable[..., float]):
        super().__init__(pathogen_sorting_strategy)

    def generate_observation_space(self) -> Space:
        single_city_obs_space = self._get_obs_space_single_city()
        complete_obs_space = self._aggregate_obs_space_over_cities(single_city_obs_space)
        return spaces.Tuple(complete_obs_space)

    def preprocess_obs(self, game_state: GameState) -> List:
        city_states = []
        sorted_game_state_pathogens = self.sort_pathogens(game_state.pathogens, game_state)
        for city in game_state.cities:
            location = (np.array([city.latitude], dtype=np.float32),
                        np.array([city.longitude], dtype=np.float32))
            population = np.array([city.population], dtype=np.uint32)
            connections = np.min((len(city.connections), MAX_CONNECTIONS))
            attributes = np.array([city.economy_strength,
                                   city.government_stability,
                                   city.hygiene_standards,
                                   city.population_awareness], dtype=np.int8)
            pathogens = self._build_pathogen_obs_representation(city.pathogens, city.population,
                                                                sorted_game_state_pathogens, game_state)
            city_states.append((location, population, connections, attributes, pathogens))

        return city_states[:MAX_CITIES]

    def sort_pathogens(self, pathogens: List[Pathogen], game_state: GameState) -> List[Pathogen]:
        """
        Sort pathogens by relevance, e.g. 7, 3, 9, 10 -> 10, 9, 7, 3
        """
        initial_value = 0
        sorted_pathogens = sorted(pathogens,
                                  reverse=True,
                                  key=lambda pathogen:
                                  reduce(lambda count, infected_population: count + infected_population,
                                         map(self.pathogen_sorting_strategy,
                                             filter(lambda city: pathogen in city.pathogens,
                                                    game_state.cities), repeat(pathogen)), initial_value))
        return sorted_pathogens[:MAX_PATHOGENS]

    def _get_obs_space_single_city(self):
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
        pathogens = build_multi_space(self._pathogen_space_representation(), 5)
        # events have been left out yet, todo: handle them when the time is right.
        return spaces.Tuple((location, population, connections, attributes, pathogens))

    @classmethod
    def _pathogen_space_representation(cls):
        return spaces.Tuple((
            Discrete(9),  # see _map_pathogen_status
            Box(low=0, high=UINT32_MAX, shape=(1,), dtype=np.uint32),  # infected-population
            Box(low=-2, high=2, shape=(4,), dtype=np.int8)  # infectivity, mobility, duration, lethality
        ))

    @classmethod
    def _aggregate_obs_space_over_cities(cls, action_space: Space):
        aggregated_space = []
        for _ in range(MAX_CITIES):
            aggregated_space.append(action_space)
        return aggregated_space

    def _build_pathogen_obs_representation(self, city_pathogens: List[Pathogen],
                                           city_population: int,
                                           sorted_gamestate_pathogens: List[Pathogen], game_state: GameState) -> tuple:
        """
        :param global_pathogens:
        :param city_population:
        :param city_pathogens: a list of pathogens for the city
        :return: a list of pathogens s.t. (is_active, infected_population, np.arr[infectivity, mobility, duration, lethality]
        """
        pathogen_representations = []
        sorted_available_pathogens = list(
            filter(lambda city_pathogen: city_pathogen in sorted_gamestate_pathogens, city_pathogens))
        for pathogen in sorted_available_pathogens[:MAX_PATHOGENS]:
            status = self._map_pathogen_status(pathogen, game_state)
            infected_population = np.array([np.round(pathogen.prevalence * city_population)], dtype=np.uint32)
            pathogen_attributes = np.array([pathogen.infectivity,
                                            pathogen.mobility,
                                            pathogen.duration,
                                            pathogen.lethality], dtype=np.int8)
            pathogen_representation = (status, infected_population, pathogen_attributes)
            pathogen_representations = self._update_city_pathogens_representations(pathogen_representations, pathogen,
                                                                                   pathogen_representation,
                                                                                   sorted_available_pathogens)

        for _ in range(MAX_PATHOGENS - len(sorted_available_pathogens[:MAX_PATHOGENS])):
            pathogen_representations.append(self._build_pathogen_stub())

        return tuple(pathogen_representations)

    @classmethod
    def _map_pathogen_status(cls, pathogen: Pathogen, game_state: GameState):
        pathogen_exists = lambda: pathogen in game_state.pathogens
        medication_in_development = lambda: pathogen in game_state.pathogens_with_medication_in_development
        vaccination_in_development = lambda: pathogen in game_state.pathogens_with_vaccination_in_development
        medication_exists = lambda: pathogen in game_state.pathogens_with_medication
        vaccination_exists = lambda: pathogen in game_state.pathogens_with_vaccination

        if medication_exists() and vaccination_exists():
            pathogen_status = 8
        elif vaccination_exists() and medication_in_development():
            pathogen_status = 7
        elif medication_exists() and vaccination_in_development():
            pathogen_status = 6
        elif vaccination_exists():
            pathogen_status = 5
        elif medication_exists():
            pathogen_status = 4
        elif vaccination_in_development():
            pathogen_status = 3
        elif medication_in_development():
            pathogen_status = 2
        elif pathogen_exists():
            pathogen_status = 1
        else:
            pathogen_status = 0

        return pathogen_status

    def _update_city_pathogens_representations(self, pathogen_list: List, pathogen: Pathogen,
                                               pathogen_representation: Tuple,
                                               sorted_available_pathogens: List[Pathogen]) -> List:
        pathogen_index = sorted_available_pathogens.index(pathogen)
        while True:
            try:
                pathogen_list[pathogen_index] = pathogen_representation
                return pathogen_list
            except IndexError:
                pathogen_list.append(self._build_pathogen_stub())

    @classmethod
    def _build_pathogen_stub(cls) -> tuple:
        inactive = 0
        infected_population = np.array([0], dtype=np.uint32)
        infectivity = 0
        mobility = 0
        duration = 0
        lethality = 0
        pathogen_attributes = np.array([infectivity, mobility, duration, lethality], dtype=np.int8)
        return inactive, infected_population, pathogen_attributes

    @classmethod
    def _get_pathogen_population(cls, game_state: GameState, pathogen: Pathogen):
        infected_cities = filter(lambda city: pathogen in city.pathogens, game_state.cities)
        infected_population_per_city = map(lambda city:
                                           city.population * list(filter(
                                               lambda city_pathogen: city_pathogen.index == pathogen.index,
                                               city.pathogens))[0].prevalence, infected_cities)
        total_infected_population = reduce(lambda accu, infected_city_pop: accu + infected_city_pop,
                                           infected_population_per_city, 0)
        return total_infected_population


def infected_population_sorting_per_city(city: City, pathogen: Pathogen) -> float:
    city_pathogen_ids = list(map(lambda city_pathogen: city_pathogen.index, city.pathogens))
    if pathogen.index in city_pathogen_ids:
        pathogen_index = city_pathogen_ids.index(pathogen.index)
        pathogen_prevalence = city.pathogens[pathogen_index].prevalence
        return city.population * pathogen_prevalence
    else:
        return 0

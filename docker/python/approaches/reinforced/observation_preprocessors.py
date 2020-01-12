import abc
from functools import reduce
from itertools import repeat
from typing import List, Tuple

import numpy as np

from approaches.reinforced.constants import MAX_PATHOGENS, MAX_CONNECTIONS
from approaches.reinforced.util import timer
from models.city import City
from models.gamestate import GameState
from models.pathogen import Pathogen


class ObservationPreprocessor(abc.ABC):
    @abc.abstractmethod
    def preprocess(self, game_state: GameState) -> list:
        pass

    @abc.abstractmethod
    def sort_pathogens(self, pathogens: List[Pathogen], cities: List[City]) -> List[Pathogen]:
        pass


# noinspection PyMethodMayBeStatic
class NaivePreprocessor(ObservationPreprocessor):
    def __init__(self):
        self.sorting_strategy = prevalence_sorting

    @timer
    def preprocess(self, game_state: GameState) -> list:
        """
        :param game_state:
        :return: tuple(tuple(lat,long), population, connections(max5), economy, gov, hygiene, populationAw, city_pathogens(max5))
        """
        city_states = []
        sorted_game_state_pathogens = self.sort_pathogens(game_state.get_pathogens(), game_state.get_cities())
        for city in game_state.get_cities():
            location = (np.array([city.get_latitude()], dtype=np.float32),
                        np.array([city.get_longitude()], dtype=np.float32))
            population = np.array([city.get_population()], dtype=np.uint32)
            connections = np.min((len(city.get_connections()), MAX_CONNECTIONS))
            attributes = np.array([city.get_economy_strength(),
                                   city.get_government_stability(),
                                   city.get_hygiene_standards(),
                                   city.get_population_awareness()], dtype=np.int8)
            pathogens = self._build_pathogens_representation(city.get_pathogens(), city.get_population(),
                                                             sorted_game_state_pathogens, game_state)
            city_states.append((location, population, connections, attributes, pathogens))

        return city_states

    def _build_pathogens_representation(self, city_pathogens: List[Pathogen],
                                        city_population: int,
                                        sorted_gamestate_pathogens: List[Pathogen], game_state: GameState) -> tuple:
        """
        :param global_pathogens:
        :param city_population:
        :param city_pathogens: a list of pathogens for the city
        :return: a list of pathogens s.t. (is_active, infected_population, np.arr[infectivity, mobility, duration, lethality]
        """
        pathogen_representations = []
        available_pathogens = list(
            filter(lambda city_pathogen: city_pathogen in sorted_gamestate_pathogens, city_pathogens))
        for pathogen in available_pathogens[:MAX_PATHOGENS]:
            status = self._map_pathogen_status(pathogen, game_state)
            infected_population = np.array([np.round(pathogen.get_prevalence() * city_population)], dtype=np.uint32)
            pathogen_attributes = np.array([pathogen.get_infectivity(),
                                            pathogen.get_mobility(),
                                            pathogen.get_duration(),
                                            pathogen.get_lethality()], dtype=np.int8)
            pathogen_representation = (status, infected_population, pathogen_attributes)
            pathogen_representations = self._update_city_pathogens_representations(pathogen_representations, pathogen,
                                                                                   pathogen_representation,
                                                                                   available_pathogens)

        for _ in range(MAX_PATHOGENS - len(city_pathogens)):
            pathogen_representations.append(self._build_pathogen_stub())

        return tuple(pathogen_representations)

    def _map_pathogen_status(self, pathogen: Pathogen, game_state: GameState):
        pathogen_exists = lambda: pathogen in game_state.get_pathogens()
        medication_in_development = lambda: game_state.get_pathogens_with_medication_in_development()
        vaccination_in_development = lambda: game_state.get_pathogens_with_vaccination_in_development()
        medication_exists = lambda: game_state.get_pathogens_with_medication()
        vaccination_exists = lambda: game_state.get_pathogens_with_vaccination()

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
                                               available_pathogens: List[Pathogen]) -> List:
        pathogen_index = available_pathogens.index(pathogen)
        while True:
            try:
                pathogen_list[pathogen_index] = pathogen_representation
                return pathogen_list
            except IndexError:
                pathogen_list.append(self._build_pathogen_stub())

    def _build_pathogen_stub(self) -> tuple:
        inactive = 0
        infected_population = np.array([0], dtype=np.uint32)
        infectivity = 0
        mobility = 0
        duration = 0
        lethality = 0
        pathogen_attributes = np.array([infectivity, mobility, duration, lethality], dtype=np.int8)
        return inactive, infected_population, pathogen_attributes

    def sort_pathogens(self, pathogens: List[Pathogen], cities: List[City]) -> List[Pathogen]:
        initial_value = 0
        sorted_pathogens = sorted(pathogens,
                                  reverse=True,
                                  key=lambda pathogen:
                                  reduce(lambda count, infected_population: count + infected_population,
                                         map(self.sorting_strategy,
                                             filter(lambda city: pathogen in city.get_pathogens(),
                                                    cities), repeat(pathogen)), initial_value))
        return sorted_pathogens

    def _get_pathogen_population(self, game_state: GameState, pathogen: Pathogen):
        infected_cities = filter(lambda city: pathogen in city.get_pathogens(), game_state.get_cities())
        infected_population_per_city = map(lambda city:
                                           city.get_population() * list(filter(
                                               lambda city_pathogen: city_pathogen.get_id() == pathogen.get_id(),
                                               city.get_pathogens()))[0].get_prevalence(), infected_cities)
        total_infected_population = reduce(lambda accu, infected_city_pop: accu + infected_city_pop,
                                           infected_population_per_city, 0)
        return total_infected_population


def prevalence_sorting(city: City, pathogen: Pathogen) -> float:
    city_pathogen_ids = list(map(lambda city_pathogen: city_pathogen.get_id(), city.get_pathogens()))
    if pathogen.get_id() in city_pathogen_ids:
        pathogen_index = city_pathogen_ids.index(pathogen.get_id())
        pathogen_prevalence = city.get_pathogens()[pathogen_index].get_prevalence()
        return city.get_population() * pathogen_prevalence
    else:
        return 0

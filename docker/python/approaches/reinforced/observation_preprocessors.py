from typing import List

import numpy as np

from approaches.reinforced.constants import MAX_PATHOGENS, MAX_CONNECTIONS
from models.gamestate import GameState
from models.pathogen import Pathogen


def naive_city_state_preprocessing(state: GameState):
    """

    :param state: the gamestate
    :return: tuple(tuple(lat,long), population, connections(max5), economy, gov, hygiene, populationAw, pathogens(max5))
    """
    city_states = []
    for city in state.get_cities():
        location = (np.array([city.get_latitude()], dtype=np.float32),
                    np.array([city.get_longitude()], dtype=np.float32))
        population = np.array([city.get_population()], dtype=np.uint32)
        connections = np.min((len(city.get_connections()), MAX_CONNECTIONS))
        attributes = np.array([city.get_economy_strength(),
                               city.get_government_stability(),
                               city.get_hygiene_standards(),
                               city.get_population_awareness()], dtype=np.int8)
        pathogens = build_pathogens_representation(city.get_pathogens(), city.get_population(), MAX_PATHOGENS)
        city_states.append((location, population, connections, attributes, pathogens))

    return city_states


def build_pathogens_representation(pathogens: List[Pathogen], city_population: int, max_len: int) -> tuple:
    """
    :param pathogens: a list of pathogens
    :param max_len:
    :return: a list of pathogens s.t. (is_active, infected_population, np.arr[infectivity, mobility, duration, lethality]
    """
    pathogen_list = []
    for pathogen in pathogens[:MAX_PATHOGENS]:
        active = 1
        infected_population = np.array([np.round(pathogen.get_prevalence() * city_population)], dtype=np.uint32)
        pathogen_attributes = np.array([pathogen.get_infectivity(),
                                        pathogen.get_mobility(),
                                        pathogen.get_duration(),
                                        pathogen.get_lethality()], dtype=np.int8)
        pathogen_list.append((active, infected_population, pathogen_attributes))

    for _ in range(max_len - len(pathogens)):
        pathogen_list.append(build_pathogen_stub())

    return tuple(pathogen_list)


def build_pathogen_stub() -> tuple:
    inactive = 0
    infected_population = np.array([0], dtype=np.uint32)
    infectivity = 0
    mobility = 0
    duration = 0
    lethality = 0
    pathogen_attributes = np.array([infectivity, mobility, duration, lethality], dtype=np.int8)
    return inactive, infected_population, pathogen_attributes

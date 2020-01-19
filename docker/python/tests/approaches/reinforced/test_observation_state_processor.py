from typing import List

import gym
import numpy as np
import pytest

from approaches.reinforced import observation_state_processor
from approaches.reinforced.constants import MAX_CITIES
from approaches.reinforced.observation_state_processor import SimpleObsStateProcessor
from models.city import City
from models.gamestate import GameState
from models.pathogen import Pathogen


@pytest.fixture
def simple_obs_state_processor(available_pathogens: List[Pathogen]) -> SimpleObsStateProcessor:
    def identity_ordering(city: City, pathogen: Pathogen) -> float:
        return available_pathogens.index(pathogen)

    return SimpleObsStateProcessor(identity_ordering)


def test_map_pathogen_status(simple_obs_state_processor: SimpleObsStateProcessor,
                             available_pathogens: List[Pathogen], gamestate_stub: GameState):
    patho0 = 5  # vaccination exists
    patho1 = 4  # medication exists
    patho2 = 8  # medication && vaccination exist
    patho3 = 6  # medication exists vaccination in dev
    patho4 = 7  # vaccination exists medication in dev
    patho_states = (patho0, patho1, patho2, patho3, patho4)
    for pathogen, patho_state in zip(available_pathogens, patho_states):
        assert simple_obs_state_processor._map_pathogen_status(pathogen, gamestate_stub) == patho_state


def test_build_pathogen_obs_representation(simple_obs_state_processor: SimpleObsStateProcessor,
                                           city_with_pathogens: City,
                                           available_pathogens: List[Pathogen],
                                           gamestate_stub: GameState):
    # GIVEN
    city_pathogens = city_with_pathogens.pathogens
    city_population = 5000

    # WHEN
    actual_pathogen_representation = simple_obs_state_processor._build_pathogen_obs_representation(city_pathogens,
                                                                                                   city_population,
                                                                                                   available_pathogens,
                                                                                                   gamestate_stub)
    # THEN
    expected_pathogen_representations = []

    # patho1
    status = 4  # medication
    infected_population = np.array([np.round(city_population * .8)], dtype=np.uint32)
    pathogen_attributes = np.array([0, 1, 2, -2], dtype=np.int8)
    expected_pathogen_representations.append((status, infected_population, pathogen_attributes))

    # patho2
    status = 8  # vaccination && medication
    infected_population = np.array([np.round(city_population * .8)], dtype=np.uint32)
    pathogen_attributes = np.array([0, 1, 2, -2], dtype=np.int8)
    expected_pathogen_representations.append((status, infected_population, pathogen_attributes))

    expected_pathogen_representations.append(simple_obs_state_processor._build_pathogen_stub())
    expected_pathogen_representations.append(simple_obs_state_processor._build_pathogen_stub())
    expected_pathogen_representations.append(simple_obs_state_processor._build_pathogen_stub())
    expected_pathogen_representations = tuple(expected_pathogen_representations)
    assert compare(actual_pathogen_representation, expected_pathogen_representations)


def compare(a, b) -> bool:
    if not isinstance(b, type(a)):
        raise TypeError('The two input objects must be of same type')
    else:
        if isinstance(a, (list, tuple)):
            for aa, bb in zip(a, b):
                if not compare(aa, bb):
                    return False  # Short circuit
            return True and len(a) == len(b)
        else:  # numpy arrays
            return np.allclose(a, b)


def test_sort_pathogens(simple_obs_state_processor: SimpleObsStateProcessor, available_pathogens: List[Pathogen],
                        gamestate_stub: GameState):
    assert (list(reversed(available_pathogens)) == simple_obs_state_processor.sort_pathogens(available_pathogens,
                                                                                             gamestate_stub))


def test_update_city_pathogens_representations(simple_obs_state_processor: SimpleObsStateProcessor,
                                               available_pathogens: List[Pathogen]):
    status = 4  # medication
    infected_population = np.array([np.round(500 * .8)], dtype=np.uint32)
    pathogen_attributes = np.array([0, 1, 2, -2], dtype=np.int8)
    pathogen_representation = (status, infected_population, pathogen_attributes)
    pathogen = available_pathogens[3]
    stub = simple_obs_state_processor._build_pathogen_stub()
    expected = [stub if i < 3 else pathogen_representation for i in range(4)]

    pathogen_list = []
    actual = simple_obs_state_processor._update_city_pathogens_representations(pathogen_list,
                                                                               pathogen,
                                                                               pathogen_representation,
                                                                               available_pathogens)
    assert compare(actual, expected) and len(actual) == len(expected)


def test_preprocess_obs(simple_obs_state_processor: SimpleObsStateProcessor, gamestate_stub: GameState,
                        available_pathogens: List[Pathogen]):
    expected_city_obs = []
    for city in gamestate_stub.cities:
        location = (np.array([90], dtype=np.float32),
                    np.array([-90], dtype=np.float32))
        population = np.array([500], dtype=np.uint32)
        connections = np.int64(2)
        attributes = np.array([0, 1, 2, -2], dtype=np.int8)
        pathogens = simple_obs_state_processor._build_pathogen_obs_representation(city.pathogens, city.population,
                                                                                  list(reversed(available_pathogens)),
                                                                                  gamestate_stub)
        expected_city_obs.append((location, population, connections, attributes, pathogens))

    actual_city_obs = simple_obs_state_processor.preprocess_obs(gamestate_stub)
    assert compare(actual_city_obs, expected_city_obs)


def test_get_pathogen_population(simple_obs_state_processor: SimpleObsStateProcessor, gamestate_stub: GameState,
                                 available_pathogens: List[Pathogen]):
    for pathogen in available_pathogens:
        assert simple_obs_state_processor._get_pathogen_population(gamestate_stub, pathogen) \
               == len(gamestate_stub.cities) * 500 * .8


def test_aggregate_obs_space_over_cities(simple_obs_state_processor: SimpleObsStateProcessor):
    example_space = gym.spaces.Discrete(5)
    assert [example_space for _ in range(MAX_CITIES)] \
           == simple_obs_state_processor._aggregate_obs_space_over_cities(example_space)


def test_infected_population_sorting_per_city(simple_obs_state_processor: SimpleObsStateProcessor,
                                              city_with_pathogens: City, available_pathogens: List[Pathogen]):
    for i, pathogen in enumerate(available_pathogens):
        if i in (1, 2):
            assert observation_state_processor.infected_population_sorting_per_city(city_with_pathogens,
                                                                                    pathogen) == .8 * city_with_pathogens.population
        else:
            assert observation_state_processor.infected_population_sorting_per_city(city_with_pathogens,
                                                                                    pathogen) == 0

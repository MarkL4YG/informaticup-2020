from typing import List, Tuple
from unittest.mock import Mock

import pytest

from models import city
from models.city import City
from models.gamestate import GameState
from models.pathogen import Pathogen


@pytest.fixture
def gamestate_stub(available_pathogens: List[Pathogen],
                   pathogens_with_medication: List[Pathogen],
                   pathogens_with_vaccination: List[Pathogen]):
    def _generate_cities() -> List[City]:
        cities = []
        for city_name in city.all_cities:
            temp_city = City(city_name)
            temp_city.pathogens = available_pathogens
            temp_city.latitude = 90
            temp_city.longitude = -90
            temp_city.population = 500
            temp_city.connections = ['Abuja', 'Accra']
            temp_city.economy_strength = 0
            temp_city.government_stability = 1
            temp_city.hygiene_standards = 2
            temp_city.population_awareness = -2

            cities.append(temp_city)
        return cities

    game_state_mock: GameState = Mock(spec=GameState,
                                      points=500,
                                      cities=_generate_cities(),
                                      pathogens=available_pathogens,
                                      pathogens_with_vaccination=pathogens_with_vaccination,
                                      pathogens_with_medication=pathogens_with_medication,
                                      pathogens_with_vaccination_in_development=[available_pathogens[3]],  # patho3
                                      pathogens_with_medication_in_development=[available_pathogens[4]]  # patho4
                                      )
    game_state_mock.get_total_population.return_value = 100

    return game_state_mock


@pytest.fixture
def available_pathogens() -> List[Pathogen]:
    patho0 = Pathogen("Pathogen:0")
    patho1 = Pathogen("Pathogen:1")
    patho2 = Pathogen("Pathogen:2")
    patho3 = Pathogen("Pathogen:3")
    patho4 = Pathogen("Pathogen:4")
    pathos = [patho0, patho1, patho2, patho3, patho4]
    for patho in pathos:
        patho.prevalence = .8
        patho.infectivity = 0
        patho.mobility = 1
        patho.duration = 2
        patho.lethality = -2
    return [patho0, patho1, patho2, patho3, patho4]


@pytest.fixture
def pathogens_with_vaccination(available_pathogens) -> List[Pathogen]:
    return available_pathogens[::2]  # patho0, patho2 and patho4


@pytest.fixture
def pathogens_with_medication(available_pathogens) -> Tuple[Pathogen, Pathogen, Pathogen]:
    # patho3, patho1 and patho2
    return available_pathogens[3], available_pathogens[1], available_pathogens[2]


@pytest.fixture
def city_with_pathogens(available_pathogens) -> City:
    sin_city = City("広島市")
    sin_city.pathogens = available_pathogens[1:3]  # patho1 and patho2
    sin_city.population = 641676
    return sin_city

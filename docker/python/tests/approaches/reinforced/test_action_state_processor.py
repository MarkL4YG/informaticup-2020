from datetime import timedelta
from typing import List, Optional
from unittest.mock import Mock

import hypothesis
import pytest
from gym import spaces
from hypothesis.strategies import integers

from approaches.reinforced.action_state_processor import SimpleActStateProcessor
from approaches.reinforced.constants import MAX_ACTIONSPACE, INVALID_ACTION, INVALID_ACTION_PENALTY, NEUTRAL_REWARD, \
    MAX_CITIES, CITY_ACTIONSPACE, GLOBAL_ACTIONSPACE, MAX_CITY_ACTIONSPACE
from models import actions
from models.actions import Action
from models.city import City
from models.gamestate import GameState
from models.pathogen import Pathogen


@pytest.fixture
def simple_act_state_processor(monkeypatch) -> SimpleActStateProcessor:
    def inverse_ordering(pathogens: List[Pathogen], game_state: GameState) -> List[Pathogen]:
        return list(reversed(pathogens))

    return SimpleActStateProcessor(inverse_ordering)


#  %%%%%%%% SimpleActStateProcessor-Tests %%%%%%%%
def test_generate_action_space(simple_act_state_processor: SimpleActStateProcessor):
    assert spaces.Discrete(MAX_ACTIONSPACE) == simple_act_state_processor.generate_action_space()


# noinspection PyProtectedMember
def test_generate_city_vaccine_actions(simple_act_state_processor: SimpleActStateProcessor,
                                       city_with_pathogens: City,
                                       available_pathogens: List[Pathogen],
                                       pathogens_with_vaccination: List[Pathogen]):
    deploy_vaccine_actions = [actions.deploy_vaccine(pathogen.index, city_with_pathogens.index)
                              if pathogen in city_with_pathogens.pathogens and pathogen in pathogens_with_vaccination
                              else INVALID_ACTION
                              for pathogen in available_pathogens]

    assert simple_act_state_processor._generate_city_vaccine_actions(city_with_pathogens,
                                                                     available_pathogens,
                                                                     pathogens_with_vaccination) == deploy_vaccine_actions

    assert simple_act_state_processor._generate_city_vaccine_actions(
        city_with_pathogens,
        available_pathogens,
        list(reversed(pathogens_with_vaccination))) == deploy_vaccine_actions

    assert simple_act_state_processor._generate_city_vaccine_actions(
        city_with_pathogens,
        list(reversed(available_pathogens)),
        pathogens_with_vaccination) == list(reversed(deploy_vaccine_actions))


def test_generate_city_med_actions(simple_act_state_processor: SimpleActStateProcessor,
                                   city_with_pathogens: City,
                                   available_pathogens: List[Pathogen],
                                   pathogens_with_medication: List[Pathogen]):
    deploy_med_actions = [actions.deploy_medication(pathogen.index, city_with_pathogens.index)
                          if (pathogen in city_with_pathogens.pathogens and pathogen in pathogens_with_medication)
                          else INVALID_ACTION
                          for pathogen in available_pathogens]

    assert simple_act_state_processor._generate_city_med_actions(city_with_pathogens,
                                                                 available_pathogens,
                                                                 pathogens_with_medication) == deploy_med_actions

    assert simple_act_state_processor._generate_city_med_actions(
        city_with_pathogens,
        available_pathogens,
        list(reversed(pathogens_with_medication))) == deploy_med_actions

    assert simple_act_state_processor._generate_city_med_actions(
        city_with_pathogens,
        list(reversed(available_pathogens)),
        pathogens_with_medication) == list(reversed(deploy_med_actions))


def test_generate_global_vaccine_actions(simple_act_state_processor: SimpleActStateProcessor,
                                         available_pathogens: List[Pathogen],
                                         pathogens_with_vaccination: List[Pathogen]):
    develop_vaccine_actions = [actions.develop_vaccine(pathogen.index)
                               if (pathogen not in pathogens_with_vaccination)
                               else INVALID_ACTION
                               for pathogen in available_pathogens]

    assert list(simple_act_state_processor._generate_global_vaccine_actions(
        available_pathogens,
        pathogens_with_vaccination)) == develop_vaccine_actions

    assert list(simple_act_state_processor._generate_global_vaccine_actions(
        available_pathogens,
        list(reversed(pathogens_with_vaccination)))) == develop_vaccine_actions

    assert list(simple_act_state_processor._generate_global_vaccine_actions(
        list(reversed(available_pathogens)), pathogens_with_vaccination)) == list(
        reversed(develop_vaccine_actions))


def test_generate_global_med_actions(simple_act_state_processor: SimpleActStateProcessor,
                                     available_pathogens: List[Pathogen],
                                     pathogens_with_medication: List[Pathogen]):
    develop_med_actions = [actions.develop_medication(pathogen.index)
                           if (pathogen not in pathogens_with_medication)
                           else INVALID_ACTION
                           for pathogen in available_pathogens]

    assert list(simple_act_state_processor._generate_global_med_actions(
        available_pathogens,
        pathogens_with_medication)) == develop_med_actions

    assert list(simple_act_state_processor._generate_global_med_actions(
        available_pathogens,
        list(reversed(pathogens_with_medication)))) == develop_med_actions

    assert list(simple_act_state_processor._generate_global_med_actions(
        list(reversed(available_pathogens)), pathogens_with_medication)) == list(reversed(develop_med_actions))


@pytest.mark.parametrize("chosen_action,possible_actions,expected_penalty", [(INVALID_ACTION,
                                                                              [actions.apply_hygienic_measures(0)],
                                                                              INVALID_ACTION_PENALTY),
                                                                             (actions.apply_hygienic_measures(0),
                                                                              [],
                                                                              INVALID_ACTION_PENALTY),
                                                                             (actions.apply_hygienic_measures(0),
                                                                              [actions.apply_hygienic_measures(0)],
                                                                              NEUTRAL_REWARD)])
def test_penalize_action(simple_act_state_processor: SimpleActStateProcessor, gamestate_stub: Mock, monkeypatch,
                         chosen_action: Optional[Action], possible_actions: List[Action], expected_penalty: int):
    # GIVEN
    monkeypatch.setattr('models.actions.generate_possible_actions', lambda _: possible_actions)
    # THEN
    assert simple_act_state_processor.penalize_action(chosen_action, gamestate_stub) \
           == (chosen_action, expected_penalty)


@hypothesis.given(random_city_id=integers(0, MAX_CITIES - 1), random_action_id=integers(0, CITY_ACTIONSPACE - 1))
def test_transform_for_city_action(simple_act_state_processor: SimpleActStateProcessor,
                                   random_city_id: int, random_action_id: int):
    action: int = random_city_id * CITY_ACTIONSPACE + random_action_id
    assert simple_act_state_processor._transform_for_city_action(action) == (random_action_id, random_city_id)


@hypothesis.settings(deadline=timedelta(seconds=10), max_examples=15)
@hypothesis.given(random_action_id=integers(0, MAX_CITY_ACTIONSPACE - 1))
def test_map_city_actions(simple_act_state_processor: SimpleActStateProcessor, gamestate_stub: GameState,
                          random_action_id: int):
    chosen_action: int = random_action_id % CITY_ACTIONSPACE
    pathogens_with_vacc_or_med = (6, 8, 10, 12, 13, 14)
    if chosen_action in range(0, 6) or chosen_action in pathogens_with_vacc_or_med:
        assert simple_act_state_processor._map_city_actions(chosen_action, gamestate_stub) \
               in actions.generate_possible_actions(gamestate_stub)
    else:
        assert simple_act_state_processor._map_city_actions(chosen_action, gamestate_stub) == INVALID_ACTION


@hypothesis.settings(deadline=timedelta(seconds=10), max_examples=15)
@hypothesis.given(random_action_id=integers(0, GLOBAL_ACTIONSPACE - 1))
def test_map_global_actions(simple_act_state_processor: SimpleActStateProcessor, gamestate_stub: GameState,
                            random_action_id: int):
    chosen_action: int = random_action_id
    pathogens_with_vacc_or_med = (1, 2, 3, 5, 6, 7, 8, 9)
    if random_action_id == 0 or random_action_id not in pathogens_with_vacc_or_med:
        assert simple_act_state_processor._map_global_actions(chosen_action, gamestate_stub) \
               in actions.generate_possible_actions(gamestate_stub)
    else:
        assert simple_act_state_processor._map_global_actions(chosen_action, gamestate_stub) == INVALID_ACTION


@hypothesis.settings(deadline=timedelta(seconds=10), max_examples=15)
@hypothesis.given(random_action_id=integers(0, MAX_ACTIONSPACE - 1))
def test_map_action(simple_act_state_processor: SimpleActStateProcessor, gamestate_stub: GameState,
                    random_action_id: int):
    if random_action_id < GLOBAL_ACTIONSPACE:
        expected = simple_act_state_processor.penalize_action(
            simple_act_state_processor._map_global_actions(random_action_id, gamestate_stub), gamestate_stub)
        assert expected == simple_act_state_processor.map_action(random_action_id, gamestate_stub)
    else:
        random_city_action_id = random_action_id - GLOBAL_ACTIONSPACE
        expected = simple_act_state_processor.penalize_action(
            simple_act_state_processor._map_city_actions(random_city_action_id, gamestate_stub), gamestate_stub)
        assert expected == simple_act_state_processor.map_action(random_action_id, gamestate_stub)

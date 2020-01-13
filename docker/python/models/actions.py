import collections

import ray

from models.city import get_city_name, get_city_id, City
from models.pathogen import get_pathogen_name


class Action:

    def __init__(self, json, cost):
        self._json = json
        self._cost = cost

    def get_json(self):
        return self._json

    def get_cost(self):
        return self._cost

    def __eq__(self, other):
        if isinstance(other, Action):
            return self._json == other._json
        else:
            return False

def end_round() -> Action:
    return Action({"type": "endRound"}, 0)


def quarantine_city(city_id, number_of_rounds=1) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "putUnderQuarantine",
        "city": city_name,
        "rounds": number_of_rounds
    }, 20 + 10 * number_of_rounds)


def close_airport(city_id, number_of_rounds=1) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "closeAirport",
        "city": city_name,
        "rounds": number_of_rounds
    }, 15 + 5 * number_of_rounds)


def close_airway(from_city_id, to_city_id, number_of_rounds=1) -> Action:
    from_city_name = get_city_name(from_city_id)
    to_city_name = get_city_name(to_city_id)
    return Action({
        "type": "closeConnection",
        "fromCity": from_city_name,
        "toCity": to_city_name,
        "rounds": number_of_rounds
    }, 3 + 3 * number_of_rounds)


def develop_vaccine(pathogen_id) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    return Action({
        "type": "developVaccine",
        "pathogen": pathogen_name
    }, 40)


def deploy_vaccine(pathogen_id, city_id) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    city_name = get_city_name(city_id)
    return Action({
        "type": "deployVaccine",
        "pathogen": pathogen_name,
        "city": city_name
    }, 5)


def develop_medication(pathogen_id) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    return Action({
        "type": "developMedication",
        "pathogen": pathogen_name
    }, 20)


def deploy_medication(pathogen_id, city_id) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    city_name = get_city_name(city_id)
    return Action({
        "type": "deployMedication",
        "pathogen": pathogen_name,
        "city": city_name
    }, 10)


def exert_political_influence(city_id) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "exertInfluence",
        "city": city_name
    }, 3)


def call_for_elections(city_id) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "callElections",
        "city": city_name
    }, 3)


def apply_hygienic_measures(city_id) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "applyHygienicMeasures",
        "city": city_name
    }, 3)


def launch_campaign(city_id) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "launchCampaign",
        "city": city_name
    }, 3)


def flatten(x):
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


def generate_possible_actions(game_state):
    actions = [end_round()]

    available_points = game_state.get_available_points()

    for city in game_state.get_cities():
        city_id = city.get_city_id()

        if available_points >= 3:
            actions.append(exert_political_influence(city_id))
            actions.append(call_for_elections(city_id))
            actions.append(apply_hygienic_measures(city_id))
            actions.append(launch_campaign(city_id))

        if available_points > 6:
            for other_city in city.get_connections():
                for i in range(1, int((available_points - 3) / 3) + 1):
                    actions.append(close_airway(city_id, get_city_id(other_city), i))

        if available_points > 20 and not city.airport_closed:
            for i in range(1, int((available_points - 15) / 5) + 1):
                actions.append(close_airport(city_id, i))

        if available_points > 30:
            for i in range(1, int((available_points - 20) / 10) + 1):
                actions.append(quarantine_city(city_id, i))

        for pathogen in game_state.get_pathogens():

            if available_points >= 5 and pathogen in game_state.get_pathogens_with_vaccination():
                actions.append(deploy_vaccine(pathogen.get_id(), city_id))

            if available_points >= 10 and pathogen in game_state.get_pathogens_with_medication():
                actions.append(deploy_medication(pathogen.get_id(), city_id))

    for pathogen in game_state.get_pathogens():

        if available_points >= 40 and pathogen not in game_state.get_pathogens_with_vaccination() \
                and pathogen not in game_state.get_pathogens_with_vaccination_in_development():
            actions.append(develop_vaccine(pathogen.get_id()))

        if available_points >= 20 and pathogen not in game_state.get_pathogens_with_medication() \
                and pathogen not in game_state.get_pathogens_with_medication_in_development():
            actions.append(develop_medication(pathogen.get_id()))

    return actions


def generate_possible_actions_parallelized(game_state):
    available_points = game_state.get_available_points()
    city_action_refs = get_all_city_actions.remote(available_points, game_state)
    gamestate_pathogen_action_refs = get_all_state_actions.remote(available_points, game_state)
    actions = ray.get([city_action_refs, gamestate_pathogen_action_refs])
    actions.append(end_round())
    return flatten(actions)


@ray.remote
def actions_gamestate_pathogens_gte40(available_points, pathogen, game_state):
    actions = []
    if available_points >= 40 and pathogen not in game_state.get_pathogens_with_vaccination() \
            and pathogen not in game_state.get_pathogens_with_vaccination_in_development():
        actions.append(develop_vaccine(pathogen.get_id()))
    return actions


@ray.remote
def actions_gamestate_pathogens_gte20(available_points, pathogen, game_state):
    actions = []
    if available_points >= 20 and pathogen not in game_state.get_pathogens_with_medication() \
            and pathogen not in game_state.get_pathogens_with_medication_in_development():
        actions.append(develop_medication(pathogen.get_id()))
    return actions


@ray.remote
def actions_city_pathogens_gte5(available_points: int, city_id, pathogen, game_state):
    actions = []
    if available_points >= 5 and pathogen in game_state.get_pathogens_with_vaccination():
        actions.append(deploy_vaccine(pathogen.get_id(), city_id))
    return actions


@ray.remote
def actions_city_pathogens_gte10(available_points: int, city_id, pathogen, game_state):
    actions = []
    if available_points >= 10 and pathogen in game_state.get_pathogens_with_medication():
        actions.append(deploy_medication(pathogen.get_id(), city_id))
    return actions


@ray.remote
def actions_gte3(available_points: int, city_id):
    actions = []
    if available_points >= 3:
        actions.append(exert_political_influence(city_id))
        actions.append(call_for_elections(city_id))
        actions.append(apply_hygienic_measures(city_id))
        actions.append(launch_campaign(city_id))
    return actions


@ray.remote
def actions_gte6(available_points: int, city_id, city):
    actions = []
    if available_points > 6:
        for other_city in city.get_connections():
            for i in range(1, int((available_points - 3) / 3) + 1):
                actions.append(close_airway(city_id, get_city_id(other_city), i))
    return actions


@ray.remote
def actions_gte20(available_points: int, city: City):
    actions = []
    if available_points > 20 and not city.airport_closed:
        for i in range(1, int((available_points - 15) / 5) + 1):
            actions.append(close_airport(city.get_city_id(), i))
    return actions


@ray.remote
def actions_gte30(available_points: int, city: City):
    actions = []
    if available_points > 30 and not city.under_quarantine:
        for i in range(1, int((available_points - 20) / 10) + 1):
            actions.append(quarantine_city(city.get_city_id(), i))
    return actions


@ray.remote
def get_all_city_actions(available_points, game_state):
    for city in game_state.get_cities():
        city_id = city.get_city_id()

        actions_gte3_ref = actions_gte3.remote(available_points, city_id)
        actions_gte6_ref = actions_gte6.remote(available_points, city_id, city)
        actions_gte20_ref = actions_gte20.remote(available_points, city)
        actions_gte30_ref = actions_gte30.remote(available_points, city)

        city_pathogen_action_refs = []
        for pathogen in game_state.get_pathogens():
            city_pathogen_action_refs.append(actions_city_pathogens_gte5.remote(available_points,
                                                                                city_id,
                                                                                pathogen,
                                                                                game_state))
            city_pathogen_action_refs.append(actions_city_pathogens_gte10.remote(available_points,
                                                                                 city_id,
                                                                                 pathogen,
                                                                                 game_state))
        city_actions = ray.get([actions_gte3_ref, actions_gte6_ref, actions_gte20_ref, actions_gte30_ref,
                                *city_pathogen_action_refs])
        return city_actions


@ray.remote
def get_all_state_actions(available_points, game_state):
    gamestate_pathogen_action_refs = []
    for pathogen in game_state.get_pathogens():
        gamestate_pathogen_action_refs.append(actions_gamestate_pathogens_gte20.remote(available_points,
                                                                                       pathogen,
                                                                                       game_state))
        gamestate_pathogen_action_refs.append(actions_gamestate_pathogens_gte40.remote(available_points,
                                                                                       pathogen,
                                                                                       game_state))
    gamestate_actions = ray.get(gamestate_pathogen_action_refs)
    return gamestate_actions

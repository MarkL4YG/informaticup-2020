import collections

from models.city import get_city_name, get_city_id
from models.gamestate import GameState
from models.pathogen import get_pathogen_name


class Action:
    def __init__(self, json, cost):
        self.json = json
        self.cost = cost

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.json == other.json
        else:
            return False

    def __hash__(self):
        return hash(self.json)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.json

    def __repr__(self):
        return f"<Action({self.json, self.cost})>"


def end_round() -> Action:
    return Action({"type": "endRound"}, 0)


def quarantine_city(city_id: int, number_of_rounds=1) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "putUnderQuarantine",
        "city": city_name,
        "rounds": number_of_rounds
    }, 20 + 10 * number_of_rounds)


def close_airport(city_id: int, number_of_rounds=1) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "closeAirport",
        "city": city_name,
        "rounds": number_of_rounds
    }, 15 + 5 * number_of_rounds)


def close_airway(from_city_id, to_city_id: int, number_of_rounds=1) -> Action:
    from_city_name = get_city_name(from_city_id)
    to_city_name = get_city_name(to_city_id)
    return Action({
        "type": "closeConnection",
        "fromCity": from_city_name,
        "toCity": to_city_name,
        "rounds": number_of_rounds
    }, 3 + 3 * number_of_rounds)


def develop_vaccine(pathogen_id: int) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    return Action({
        "type": "developVaccine",
        "pathogen": pathogen_name
    }, 40)


def deploy_vaccine(pathogen_id: int, city_id: int) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    city_name = get_city_name(city_id)
    return Action({
        "type": "deployVaccine",
        "pathogen": pathogen_name,
        "city": city_name
    }, 5)


def develop_medication(pathogen_id: int) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    return Action({
        "type": "developMedication",
        "pathogen": pathogen_name
    }, 20)


def deploy_medication(pathogen_id: int, city_id: int) -> Action:
    pathogen_name = get_pathogen_name(pathogen_id)
    city_name = get_city_name(city_id)
    return Action({
        "type": "deployMedication",
        "pathogen": pathogen_name,
        "city": city_name
    }, 10)


def exert_political_influence(city_id: int) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "exertInfluence",
        "city": city_name
    }, 3)


def call_for_elections(city_id: int) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "callElections",
        "city": city_name
    }, 3)


def apply_hygienic_measures(city_id: int) -> Action:
    city_name = get_city_name(city_id)
    return Action({
        "type": "applyHygienicMeasures",
        "city": city_name
    }, 3)


def launch_campaign(city_id: int) -> Action:
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


def generate_possible_actions(game_state: GameState):
    actions = [end_round()]
    available_points = game_state.points

    for city in game_state.cities:
        city_id = city.index

        if available_points >= 3:
            actions.append(exert_political_influence(city_id))
            actions.append(call_for_elections(city_id))
            actions.append(apply_hygienic_measures(city_id))
            actions.append(launch_campaign(city_id))

        if available_points > 6:
            for other_city in city.connections:
                for i in range(1, int((available_points - 3) / 3) + 1):
                    actions.append(close_airway(city_id, get_city_id(other_city), i))

        if available_points > 20 and not city.airport_closed:
            for i in range(1, int((available_points - 15) / 5) + 1):
                actions.append(close_airport(city_id, i))

        if available_points > 30 and not city.under_quarantine:
            for i in range(1, int((available_points - 20) / 10) + 1):
                actions.append(quarantine_city(city_id, i))

        for pathogen in game_state.pathogens:

            if available_points >= 5 and pathogen in game_state.pathogens_with_vaccination:
                actions.append(deploy_vaccine(pathogen.index, city_id))

            if available_points >= 10 and pathogen in game_state.pathogens_with_medication:
                actions.append(deploy_medication(pathogen.index, city_id))

    for pathogen in game_state.pathogens:

        if available_points >= 40 and pathogen not in game_state.pathogens_with_vaccination \
                and pathogen not in game_state.pathogens_with_vaccination_in_development:
            actions.append(develop_vaccine(pathogen.index))

        if available_points >= 20 and pathogen not in game_state.pathogens_with_medication \
                and pathogen not in game_state.pathogens_with_medication_in_development:
            actions.append(develop_medication(pathogen.index))

    return actions

from models.actions import exert_political_influence, call_for_elections, apply_hygienic_measures, launch_campaign, \
    end_round
from models.gamestate import GameState


class Action:
    def __init__(self, effectiveness, action):
        self.effectiveness = effectiveness
        self.action = action


def calculate_priority_random(population, score):
    if score == -2:
        return population * 4
    if score == -1:
        return population * 3
    if score == 0:
        return population
    else:
        return 0


def calculate_priority_increase(population, score):
    return population * (2 - score)


def process_round(state: GameState):
    if state.get_available_points() >= 3:
        cities = state.get_cities()
        round = state.get_round()
        possible_actions = []

        for city in cities:
            events = city.get_events()

            influence_events = list(
                filter(lambda event: event.get_event_type() == "influenceExerted" and event.get_round() == round,
                       events))
            if not influence_events:
                influence_priority = calculate_priority_random(city.get_population(), city.get_economy_strength())
                possible_actions.append(Action(influence_priority, exert_political_influence(city.get_city_id())))

            elections_events = list(
                filter(lambda event: event.get_event_type() == "electionsCalled" and event.get_round() == round,
                       events))
            if not elections_events:
                elections_priority = calculate_priority_random(city.get_population(), city.get_government_stability())
                possible_actions.append(Action(elections_priority, call_for_elections(city.get_city_id())))

            hygienic_events = list(
                filter(lambda event: event.get_event_type() == "hygienicMeasuresApplied" and event.get_round() == round,
                       events))
            if not hygienic_events:
                hygienic_priority = calculate_priority_increase(city.get_population(), city.get_hygiene_standards())
                possible_actions.append(Action(hygienic_priority, apply_hygienic_measures(city.get_city_id())))

            campaign_events = list(
                filter(lambda event: event.get_event_type() == "campaignLaunched" and event.get_round() == round,
                       events))
            if not campaign_events:
                campaign_priority = calculate_priority_increase(city.get_population(), city.get_population_awareness())
                possible_actions.append(Action(campaign_priority, launch_campaign(city.get_city_id())))

        if possible_actions:
            possible_actions.sort(key=lambda action: action.effectiveness, reverse=True)
            return possible_actions[0].action
        else:
            return end_round()
    else:
        return end_round()

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


def get_events_in_current_round(events, event_type, current_round):
    return list(filter(lambda event: event.event_type == event_type and event.round == current_round, events))


def process_round(state: GameState):
    if state.points >= 3:
        cities = state.cities
        current_round = state.round
        possible_actions = []

        for city in cities:
            events = city.events

            influence_events = get_events_in_current_round(events, "influenceExerted", current_round)
            if not influence_events:
                influence_priority = calculate_priority_random(city.population, city.economy_strength)
                possible_actions.append(Action(influence_priority, exert_political_influence(city.index)))

            elections_events = get_events_in_current_round(events, "electionsCalled", current_round)
            if not elections_events:
                elections_priority = calculate_priority_random(city.population, city.government_stability)
                possible_actions.append(Action(elections_priority, call_for_elections(city.index)))

            hygienic_events = get_events_in_current_round(events, "hygienicMeasuresApplied", current_round)
            if not hygienic_events:
                hygienic_priority = calculate_priority_increase(city.population, city.hygiene_standards)
                possible_actions.append(Action(hygienic_priority, apply_hygienic_measures(city.index)))

            campaign_events = get_events_in_current_round(events, "campaignLaunched", current_round)
            if not campaign_events:
                campaign_priority = calculate_priority_increase(city.population, city.population_awareness)
                possible_actions.append(Action(campaign_priority, launch_campaign(city.index)))

        if possible_actions:
            possible_actions.sort(key=lambda action: action.effectiveness, reverse=True)
            return possible_actions[0].action
        else:
            return end_round()
    else:
        return end_round()

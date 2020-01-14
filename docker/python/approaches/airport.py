from models.actions import close_airway, close_airport, end_round
from models.city import City
from models.gamestate import GameState


class Action:
    def __init__(self, effectiveness, action):
        self.effectiveness = effectiveness
        self.action = action


def get_city_for_name(cities, city_name) -> City:
    return list(filter(lambda city: city.name == city_name, cities))[0]


def calculate_priority_for_connection(infected_city, uninfected_city, pathogen):
    outbreaks_of_pathogen = list(
        filter(lambda event: event.event_type == "outbreak" and event.pathogen == pathogen,
               infected_city.events))
    infected_population = outbreaks_of_pathogen[0].prevalence * infected_city.population
    uninfected_population = uninfected_city.population
    pathogen_spread = (pathogen.infectivity + 3) * (pathogen.mobility + 3)
    return infected_population * uninfected_population * pathogen_spread


def cost_for_connection_close(rounds):
    return 3 + (rounds * 3)


def cost_for_airport_close(rounds):
    return 15 + (rounds * 5)


def get_open_connections_for_city(city):
    closed_connections = list(map(lambda event: event.city, filter(
        lambda event: event.event_type == "connectionClosed",
        city.events)))
    return list(filter(lambda connection: connection not in closed_connections, city.connections))


def process_round(state: GameState):
    cities = state.cities
    available_points = state.points
    possible_actions = []

    for city in cities:
        priority_for_city = 0
        pathogens_in_city = city.pathogens
        connected_cities = list(map(lambda connection_name: get_city_for_name(cities, connection_name),
                                    get_open_connections_for_city(city)))
        airport_open = not city.airport_closed

        for other_city in connected_cities:
            priority_for_connection = 0
            pathogens_in_other_city = other_city.pathogens

            for pathogen_in_city in set(pathogens_in_city).difference(pathogens_in_other_city):
                priority_for_connection += calculate_priority_for_connection(city, other_city, pathogen_in_city)

            # the closing of a connection, unlike the closing of an airport, is not bidirectional
            rounds = 1
            while available_points >= cost_for_connection_close(rounds):
                effectiveness = priority_for_connection * rounds / cost_for_connection_close(rounds)
                action = close_airway(city.index, other_city.index, rounds)
                possible_actions.append(Action(effectiveness, action))
                rounds += 1

        if airport_open:
            for other_city in map(lambda city_name: get_city_for_name(cities, city_name), city.connections):
                priority_for_connection = 0
                pathogens_in_other_city = other_city.pathogens

                for pathogen_in_other_city in set(pathogens_in_other_city).difference(pathogens_in_city):
                    priority_for_connection += calculate_priority_for_connection(other_city, city,
                                                                                 pathogen_in_other_city)

                priority_for_city += priority_for_connection

            rounds = 1
            while available_points >= cost_for_airport_close(rounds):
                effectiveness = priority_for_city * rounds / cost_for_airport_close(rounds)
                action = close_airport(city.index, rounds)
                possible_actions.append(Action(effectiveness, action))
                rounds += 1

    if possible_actions:
        possible_actions.sort(key=lambda action: action.effectiveness, reverse=True)
        chosen_action = possible_actions[0]
        if chosen_action.effectiveness > 0:
            return chosen_action.action
        else:
            return end_round()
    else:
        return end_round()

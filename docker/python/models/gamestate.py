from functools import reduce
from models.city import City
from models.event import Event


class GameState:
    round: int = 0
    outcome: str = 'pending'
    points: int = 0
    cities: list = []
    global_events: list = []
    pathogens: list = []
    pathogens_with_medication: list = []
    pathogens_with_vaccination: list = []
    pathogens_with_medication_in_development: list = []
    pathogens_with_vaccination_in_development: list = []
    error: object = None

    def get_total_population(self):
        return reduce(lambda count, city_population: count + city_population,
                      map(lambda city: city.population, self.cities))

    def get_total_infected_population(self):
        return reduce(lambda count, city_infected: count + city_infected,
                      map(lambda city: city.infected_population, self.cities))

    def get_total_healthy_population(self):
        return self.get_total_population() - self.get_total_infected_population()


def state_from_json(json) -> GameState:
    state: GameState = GameState()
    state._round = json['round']
    state._outcome = json['outcome']
    state._points = json['points']
    for cityJson in json['cities'].values():
        city = City.from_json(cityJson)
        state.cities.append(city)

    for eventJson in json['events']:
        event: Event = Event.from_json(eventJson)
        state.global_events.append(event)

        if event.event_type == 'pathogenEncountered':
            state.pathogens.append(event.pathogen)
        elif event.event_type == 'vaccineInDevelopment':
            state.pathogens_with_vaccination_in_development.append(event.pathogen)
        elif event.event_type == 'vaccineAvailable':
            state.pathogens_with_vaccination.append(event.pathogen)
        elif event.event_type == 'medicationAvailable':
            state.pathogens_with_medication.append(event.pathogen)
        elif event.event_type == 'medicationInDevelopment':
            state.pathogens_with_medication_in_development.append(event.pathogen)

    return state

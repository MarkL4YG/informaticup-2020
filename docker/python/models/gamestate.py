from functools import reduce
from models.city import City
from models.event import Event


class GameState:

    def __init__(self):
        self.round: int = 0
        self.outcome: str = 'pending'
        self.points: int = 0
        self.cities: list = []
        self.global_events: list = []
        self.pathogens: list = []
        self.pathogens_with_medication: list = []
        self.pathogens_with_vaccination: list = []
        self.pathogens_with_medication_in_development: list = []
        self.pathogens_with_vaccination_in_development: list = []
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
    state.round = json['round']
    state.outcome = json['outcome']
    state.points = json['points']
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

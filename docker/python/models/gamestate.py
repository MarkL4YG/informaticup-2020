from functools import reduce
from models.city import City
from models.event import Event


class GameState:

    def __init__(self) -> None:
        super().__init__()
        self._round = 0
        self._outcome = "pending"
        self._points = 0
        self._cities = []
        self._global_events = []
        self._pathogens = []
        self._pathogens_with_medication = []
        self._pathogens_with_vaccination = []
        self._pathogens_with_vaccination_in_development = []
        self._pathogens_with_medication_in_development = []
        self._error = None

    def get_round(self):
        return self._round

    def get_outcome(self):
        return self._outcome

    def get_available_points(self):
        return self._points

    def get_cities(self):
        return self._cities

    def get_global_events(self):
        return self._global_events

    def get_pathogens(self):
        return self._pathogens

    def get_pathogens_with_vaccination(self):
        return self._pathogens_with_vaccination

    def get_pathogens_with_vaccination_in_development(self):
        return self._pathogens_with_vaccination_in_development

    def get_pathogens_with_medication(self):
        return self._pathogens_with_medication

    def get_pathogens_with_medication_in_development(self):
        return self._pathogens_with_medication_in_development

    def get_error(self):
        return self._error

    def get_total_population(self):
        return reduce(lambda count, city_population: count + city_population,
                      map(lambda city: city.get_population(), self.get_cities()))

    def get_total_infected_population(self):
        return reduce(lambda count, city_infected: count + city_infected,
               map(lambda city: city.get_infected_population(), self.get_cities()))

    def get_total_healthy_population(self):
        return self.get_total_population() - self.get_total_infected_population()


def state_from_json(json) -> GameState:
    state = GameState()
    state._round = json['round']
    state._outcome = json['outcome']
    state._points = json['points']
    for cityJson in json['cities'].values():
        city = City.from_json(cityJson)
        state.get_cities().append(city)

    for eventJson in json['events']:
        event = Event.from_json(eventJson)
        state.get_global_events().append(event)

        if event.get_event_type() == 'pathogenEncountered':
            state.get_pathogens().append(event.get_pathogen())
        elif event.get_event_type() == 'vaccineInDevelopment':
            state.get_pathogens_with_vaccination_in_development().append(event.get_pathogen())
        elif event.get_event_type() == 'vaccineAvailable':
            state.get_pathogens_with_vaccination().append(event.get_pathogen())
        elif event.get_event_type() == 'medicationAvailable':
            state.get_pathogens_with_medication().append(event.get_pathogen())
        elif event.get_event_type() == 'medicationInDevelopment':
            state.get_pathogens_with_medication_in_development().append(event.get_pathogen())

    return state

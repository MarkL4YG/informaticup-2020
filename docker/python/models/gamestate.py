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

    def get_error(self):
        return self._error


def state_from_json(json) -> GameState:
    state = GameState()
    state._round = json['round']
    state._outcome = json['outcome']
    state._points = json['points']
    for cityJson in json['cities'].values():
        city = City.from_json(cityJson)
        state.get_cities().append(city)

    for eventJson in json['events'].values():
        event = Event.from_json(eventJson)
        state.get_global_events().append(event)

    return state

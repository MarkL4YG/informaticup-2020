from models.city import City


class GameState:

    def __init__(self) -> None:
        super().__init__()
        self._round = 0
        self._outcome = "pending"
        self._points = 0
        self._cities = []
        self._events = {}
        self._error = None

    def get_round(self):
        return self._round

    def get_outcome(self):
        return self._outcome

    def get_available_points(self):
        return self._points

    def get_cities(self):
        return self._cities

    def get_events(self):
        return self._events

    def get_error(self):
        return self._error


def state_from_json(json) -> GameState:
    state = GameState()
    state._round = json['round']
    state._outcome = json['outcome']
    state._points = json['points']
    for cityName, cityJson in json['cities']:
        city = City.from_json(cityName, cityJson)
        state.get_cities().__add__(city)
    return state

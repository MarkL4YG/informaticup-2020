from models.pathogen import Pathogen

known_event_types = [
    # City-Events
    "outbreak",
    "uprising",
    "campaignLaunched",
    "electionsCalled",
    "influenceExerted",
    "hygienicMeasuresApplied",
    "medicationDeployed",
    "antiVaccinationism",
    "largeScalePanic",
    "economicCrisis",
    "airportClosed",
    "connectionClosed",
    "bioTerrorism",

    # Global events
    "pathogenEncountered",
    "vaccineInDevelopment",
    "vaccineAvailable",
    "medicationAvailable"
]


class Event:

    def __init__(self):
        super().__init__()
        self._eventType = None
        self._sinceRound = 0
        self._untilRound = 0
        self._round = 0
        self._pathogen = None
        self._prevalence = 0.0
        self._participants = 0
        self._city = None

    def get_event_type(self):
        return self._eventType

    def get_since_round(self):
        return self._sinceRound

    def get_until_round(self):
        return self._untilRound

    def get_round(self):
        return self._round

    def get_pathogen(self):
        return self._pathogen

    def get_prevalence(self):
        return self._prevalence

    def get_participants(self):
        return self._participants

    def get_city(self):
        return self._city

    @staticmethod
    def from_json(event_json):
        event = Event()
        event._eventType = event_json['type']
        if event.get_event_type() not in known_event_types:
            known_event_types.append(event.get_event_type())
            params = []
            for key in event_json:
                params.append(key)
            print(f'NEW EVENT_TYPE DISCOVERED! {event.get_event_type()} w/ params: {params}')

        if 'sinceRound' in event_json:
            event._sinceRound = int(event_json['sinceRound'])

        if 'untilRound' in event_json:
            event._untilRound = int(event_json['untilRound'])

        if 'round' in event_json:
            event._round = int(event_json['round'])

        if 'pathogen' in event_json:
            event._pathogen = Pathogen.from_json(event_json['pathogen'])

        if 'participants' in event_json:
            event._participants = int(event_json['participants'])

        if 'prevalence' in event_json:
            event._prevalence = event_json['prevalence']

        if 'city' in event_json:
            event._city = event_json['city']

        return event

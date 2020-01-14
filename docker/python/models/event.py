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
    "medicationInDevelopment",
    "vaccineAvailable",
    "medicationAvailable"
]


class Event:

    def __init__(self):
        self.event_type: str = None
        self.since_round: int = 0
        self.until_round: int = 0
        self.pathogen: Pathogen = None
        self.prevalence: float = 0.0
        self.participants: int = 0
        self.city = None

    def get_city(self):
        return self._city

    @staticmethod
    def from_json(event_json):
        event = Event()
        event.event_type = event_json['type']
        if event.event_type not in known_event_types:
            known_event_types.append(event.event_type)
            params = []
            for key in event_json:
                params.append(key)
            print(f'NEW EVENT_TYPE DISCOVERED! {event.event_type} w/ params: {params}')

        if 'sinceRound' in event_json:
            event.since_round = int(event_json['sinceRound'])

        if 'untilRound' in event_json:
            event.until_round = int(event_json['untilRound'])

        if 'untilRound' in event_json:
            event._untilRound = int(event_json['untilRound'])

        if 'pathogen' in event_json:
            event.pathogen = Pathogen.from_json(event_json['pathogen'])

        if 'participants' in event_json:
            event.participants = int(event_json['participants'])

        if 'prevalence' in event_json:
            event.prevalence = event_json['prevalence']

        if 'city' in event_json:
            event._city = event_json['city']

        return event

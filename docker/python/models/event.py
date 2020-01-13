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

    event_type: str = None
    since_round: int = 0
    pathogen: Pathogen = None
    prevalence: float = 0.0
    participants: int = 0

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

        if 'pathogen' in event_json:
            event.pathogen = Pathogen.from_json(event_json['pathogen'])

        if 'participants' in event_json:
            event.participants = int(event_json['participants'])

        if 'prevalence' in event_json:
            event.prevalence = event_json['prevalence']

        return event

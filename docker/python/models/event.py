from models.pathogen import Pathogen


class Event:

    def __init__(self):
        super().__init__()
        self._eventType = None
        self._sinceRound = 0
        self._pathogen = None
        self._prevalence = 0.0
        self._participants = 0

    def get_event_type(self):
        return self._eventType

    def get_since_round(self):
        return self._sinceRound

    def get_pathogen(self):
        return self._pathogen

    def get_prevalence(self):
        return self._prevalence

    def get_participants(self):
        return self._participants

    @staticmethod
    def from_json(event_json):
        event = Event()
        event._eventType = event_json['type']
        event._sinceRound = int(event_json['sinceRound'])

        if 'pathogen' in event_json:
            event._pathogen = Pathogen.from_json(event_json['pathogen'])

        if 'participants' in event_json:
            event._participants = int(event_json['participants'])

        return event

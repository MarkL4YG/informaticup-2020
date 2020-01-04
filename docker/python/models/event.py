
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

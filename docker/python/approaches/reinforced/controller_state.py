import uuid

import numpy as np


class ControllerState:
    def __init__(self):
        self._eid = uuid.uuid4().hex
        self.previous_action_penalty = 0
        self.previous_population = np.inf
        self.previous_infected_population = np.inf
        self.previous_points = 0
        self.is_first_round = True
        self.invalid_action_count = 0

    @property
    def eid(self):
        return self._eid

    def new_eid(self):
        self._eid = uuid.uuid4().hex

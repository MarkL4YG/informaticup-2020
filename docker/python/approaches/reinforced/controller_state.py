import uuid

import numpy as np


class ControllerState:
    def __init__(self):
        self._eid = uuid.uuid4().hex
        self._previous_penalty = 0
        self._previous_population = np.inf
        self._previous_infected_population = np.inf
        self._previous_points = 0
        self._is_first_round = True

    @property
    def eid(self):
        return self._eid

    def new_eid(self):
        self._eid = uuid.uuid4().hex

    @property
    def previous_penalty(self):
        return self._previous_penalty

    @previous_penalty.setter
    def previous_penalty(self, penalty):
        self._previous_penalty = penalty

    @property
    def previous_population(self):
        return self._previous_population

    @previous_population.setter
    def previous_population(self, current_population):
        self._previous_population = current_population

    @property
    def previous_infected_population(self):
        return self._previous_infected_population

    @previous_infected_population.setter
    def previous_infected_population(self, current_infected_population):
        self._previous_infected_population = current_infected_population

    @property
    def previous_points(self):
        return self._previous_points

    @previous_points.setter
    def previous_points(self, current_points):
        self._previous_points = current_points

    @property
    def is_first_round(self):
        return self._is_first_round

    @is_first_round.setter
    def is_first_round(self, is_first_round):
        self._is_first_round = is_first_round

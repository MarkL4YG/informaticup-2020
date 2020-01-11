import abc

import numpy as np

from approaches.reinforced.controller_state import ControllerState
from models.gamestate import GameState


class RewardFunction(abc.ABC):
    @abc.abstractmethod
    def calculate_reward(self, state: GameState, controller: ControllerState) -> float:
        pass


class SimpleReward(RewardFunction):
    def calculate_reward(self, state: GameState, controller: ControllerState) -> float:
        population = state.get_total_population()
        population_ratio = population / controller.previous_population
        population_score = np.log(population_ratio * state.get_round())

        return population_score + controller.previous_penalty - state.get_available_points()


def sigmoid(self, x: float, smoothing_factor: float = 1):
    return 1 / (1 + smoothing_factor * np.exp(-x))

import abc
import math

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
        population_score = math.log(population_ratio * state.round)

        return math.tanh(population_score + controller.previous_penalty - state.points)


def sigmoid(x: float, smoothing_factor: float = 1):
    return 1 / (1 + smoothing_factor * math.exp(-x))

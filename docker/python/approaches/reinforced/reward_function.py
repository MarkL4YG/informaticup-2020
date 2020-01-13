import abc
import math

import numpy as np

from approaches.reinforced.controller_state import ControllerState
from models.gamestate import GameState


class RewardFunction(abc.ABC):
    @abc.abstractmethod
    def calculate_reward(self, state: GameState, controller: ControllerState) -> float:
        pass


class SimpleReward(RewardFunction):
    def calculate_reward(self, state: GameState, controller: ControllerState) -> float:
        """
        Penalize: Rate of decrease in population
        Reward: Rate of decrease in new infections normalized by population decrease
        - assuming population can only decrease for stability.


        :param state:
        :param controller:
        :return:
        """
        m_eps = np.finfo(np.float32).eps  # prevent division over 0. everywhere - although improbable. you never know.
        d_eps = 1  # discrete epsilon for everything with populations
        population = state.get_total_population()
        population_ratio = population / (controller.previous_population + d_eps)
        population_score = math.log(population_ratio)

        infected_population = state.get_total_infected_population()

        population_delta = controller.previous_population - population
        clipped_pop_delta = np.clip(population_delta, d_eps, np.max(controller.previous_population, population))
        infected_delta = controller.previous_infected_population - infected_population
        delta_ratio = infected_delta / clipped_pop_delta

        infected_population_ratio = infected_population / (controller.previous_infected_population + d_eps)
        normalized_infected_population_ratio = infected_population_ratio * delta_ratio
        infected_score = math.log(1 / (normalized_infected_population_ratio + m_eps))

        return math.tanh(population_score
                         + infected_score
                         + controller.previous_action_penalty
                         - (state.get_available_points() / 1000))


def sigmoid(x: float, smoothing_factor: float = 1):
    return 1 / (1 + smoothing_factor * math.exp(-x))

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
        Reward: Rate of decrease in new infections normalized by approx dead infected

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

        infected_delta = controller.previous_infected_population - infected_population
        approx_dead_inf = int(controller.previous_infected_population / population_ratio) \
                          - controller.previous_infected_population
        pessimistic_weighting = 1
        if infected_delta > 0 and approx_dead_inf >= 0:  # therefore, less ill than before
            no_longer_infected = infected_delta
            # 1 - (cured-but-unfortunately-also-very-dead-ratio)
            pessimistic_weighting = np.max([1 - (approx_dead_inf / no_longer_infected), 0])

        # gt 1 => less infected this round than in previous.
        infected_population_ratio = controller.previous_infected_population / (infected_population + d_eps)
        normalized_infected_population_ratio = infected_population_ratio * pessimistic_weighting
        infected_score = math.log(normalized_infected_population_ratio + m_eps)

        return math.tanh(population_score
                         + infected_score
                         + controller.previous_action_penalty
                         - (state.points / 1000))


def sigmoid(x: float):
    """
    Stable sigmoid. Following from: 1 / (1 + exp(-x)) == exp(x) / (exp(x) + 1)
    """
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    else:
        x_exp = math.exp(x)
        return x_exp / (1 + x_exp)

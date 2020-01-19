from enum import Enum

from ray.rllib.agents.a3c import A2CTrainer

from approaches.reinforced_approach import ReinforcedApproach


# noinspection PyPep8Naming
class ml_a2c(ReinforcedApproach):
    class Weights(Enum):
        a2c4 = 'todo'

    trial_max = 10

    def __init__(self, weights: Weights = Weights.a2c4):
        super().__init__(A2CTrainer, weights.value)

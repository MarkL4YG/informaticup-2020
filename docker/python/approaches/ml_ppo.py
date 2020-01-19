from enum import Enum

from ray.rllib.agents.ppo import PPOTrainer

from approaches.reinforced_approach import ReinforcedApproach


# noinspection PyPep8Naming
class ml_ppo(ReinforcedApproach):
    class Weights(Enum):
        ppo3_323 = '../weights/ppo3_323/checkpoint-323'
        ppo5_318 = '../weights/ppo5_318/checkpoint-318'
        ppo6_303 = '../weights/ppo6_303/checkpoint-303'

    def __init__(self, weights: Weights = Weights.ppo6_303):
        super().__init__(PPOTrainer, weights.value)
        print("hello_world")

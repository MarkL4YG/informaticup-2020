from enum import Enum

from ray.rllib.agents.ppo import PPOTrainer

from approaches.reinforced_approach import ReinforcedApproach


# noinspection PyPep8Naming
class ml_ppo(ReinforcedApproach):
    class Weights(Enum):
        ppo3_323 = '../../weights/ppo3-323'

    def __init__(self, weights: Weights = Weights.ppo3_323):
        super().__init__(PPOTrainer, weights.value)
        print("hello_world")

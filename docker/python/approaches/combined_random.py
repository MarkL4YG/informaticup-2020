import importlib
import random

from approaches.approach import Approach
from models.gamestate import GameState


# noinspection PyPep8Naming
class combined_random(Approach):
    def process_round(self, state: GameState):
        possible_approaches = ["medication_and_vaccine", "airport", "city_stats"]
        return self.choose_random_approach_and_process(possible_approaches, state)

    def choose_random_approach_and_process(self, approaches, state):
        chosen_approach = random.choice(approaches)
        return importlib.import_module(f'.{chosen_approach}', "approaches").process_round(state)

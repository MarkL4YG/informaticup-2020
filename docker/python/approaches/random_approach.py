import random

from approaches.approach import Approach
from models.actions import generate_possible_actions
from models.gamestate import GameState


# noinspection PyPep8Naming
class random_approach(Approach):
    def process_round(self, state: GameState):
        # process a round and generate actions
        possible_actions = generate_possible_actions(state)
        affordable_actions = list(possible_actions)
        return random.choice(affordable_actions)

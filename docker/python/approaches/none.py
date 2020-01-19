from approaches.approach import Approach
from models.actions import end_round

from models.gamestate import GameState


# noinspection PyPep8Naming
class none(Approach):
    def process_round(self, state: GameState):
        return end_round()

import abc

from models.actions import Action
from models.gamestate import GameState


class Approach(abc.ABC):
    @abc.abstractmethod
    def process_round(self, state: GameState) -> Action:
        pass

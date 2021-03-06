from approaches.combined_random import combined_random
from models.gamestate import GameState


# noinspection PyPep8Naming
class combined_airport_vaccine_random(combined_random):
    def process_round(self, state: GameState):
        possible_approaches = ["vaccine", "airport"]
        return self.choose_random_approach_and_process(possible_approaches, state)

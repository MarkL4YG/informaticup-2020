from approaches.combined_random import combined_random
from models.gamestate import GameState


# noinspection PyPep8Naming
class combined_airport_city_stats_random(combined_random):
    def process_round(self, state: GameState):
        possible_approaches = ["city_stats", "airport"]
        return self.choose_random_approach_and_process(possible_approaches, state)

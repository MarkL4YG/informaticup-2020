from approaches.combined.combined_random import choose_random_approach_and_process
from models.gamestate import GameState


def process_round(state: GameState):
    possible_approaches = ["medication_and_vaccine", "city_stats"]
    return choose_random_approach_and_process(possible_approaches, state)

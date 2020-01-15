import importlib
import random

from models.gamestate import GameState


def choose_random_approach_and_process(approaches, state):
    chosen_approach = random.choice(approaches)
    return importlib.import_module(f'.{chosen_approach}', "approaches").process_round(state)


def process_round(state: GameState):
    possible_approaches = ["medication_and_vaccine", "airport", "city_stats"]
    return choose_random_approach_and_process(possible_approaches, state)

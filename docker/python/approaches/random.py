import random

from models.actions import generate_possible_actions


def process_round(state):
    # process a round and generate actions
    possible_actions = generate_possible_actions(state)
    affordable_actions = list(possible_actions)
    return random.choice(affordable_actions)

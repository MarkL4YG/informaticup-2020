import random

from models.actions import generate_possible_actions


def process_round(state):
    # process a round and generate actions
    available_points = state.get_available_points()
    possible_actions = generate_possible_actions(state)
    affordable_actions = list(filter(lambda action: action.get_cost() <= available_points, possible_actions))
    return random.choice(affordable_actions)

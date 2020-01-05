import random
from typing import List, Any

from bottle import post, request, run, BaseRequest

from docker.python.models.actions import generate_possible_actions, end_round
from docker.python.models.gamestate import state_from_json
import os

from docker.python.models.round import Round

LOG_FILE = "../../log.txt"
rounds: List[Round] = []

def log_to_file(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f'{text}\n')


def clear_log_file():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")


def process_round(state):
    # process a round and generate actions
    available_points = state.get_available_points()
    possible_actions = generate_possible_actions(state)
    affordable_actions = list(filter(lambda action: action.get_cost() <= available_points, possible_actions))
    return random.choice(affordable_actions)


def process_game_end(rounds):
    # process end of game
    rounds.clear()


@post("/")
def index():
    game_json = request.json
    log_to_file(game_json)
    state = state_from_json(game_json)
    print(f'round: {state.get_round()}, points: {state.get_available_points()}, outcome: {state.get_outcome()}')
    if state.get_outcome() == 'pending':
        action = process_round(state)
        rounds.append(Round(state, action))
        print(action.get_json())
        log_to_file(action)
        log_to_file("")
        return action
    else:
        process_game_end(rounds)
        return end_round()


clear_log_file()

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
port = int(os.getenv('SERVER_PORT', '50123'))
print(f'Pandemic-Player listening to 0.0.0.0:{port}', flush=True)
run(host="0.0.0.0", port=port, quiet=True)

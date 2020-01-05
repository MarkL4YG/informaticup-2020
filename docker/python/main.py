import random
from typing import List, Any

from bottle import post, request, run, BaseRequest

from docker.python.models.actions import Actions
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
    action = random.choice(Actions.generate_possible_actions(state))
    print(action)
    return action


def process_game_end(rounds):
    # process end of game
    rounds.clear()


@post("/")
def index():
    game_json = request.json
    log_to_file(game_json)
    state = state_from_json(game_json)
    print(f'round: {state.get_round()}, outcome: {state.get_outcome()}')
    if state.get_outcome() == 'pending':
        actions = process_round(state)
        rounds.append(Round(state, actions))
        log_to_file(actions)
        log_to_file("")
        return actions
    else:
        process_game_end(rounds)
        return Actions.end_round()


clear_log_file()

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
port = int(os.getenv('SERVER_PORT', '50123'))
print(f'Pandemic-Player listening to 0.0.0.0:{port}', flush=True)
run(host="0.0.0.0", port=port, quiet=True)

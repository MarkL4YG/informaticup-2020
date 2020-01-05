import csv
import random
from typing import List, Any

from bottle import post, request, run, BaseRequest

from docker.python.models.actions import generate_possible_actions, end_round
from docker.python.models.gamestate import state_from_json
import os

LOG_FILE = "../../output/log.txt"


def log_to_file(text):
    if os.getenv('LOG_ACTIONS', 'FALSE') == "TRUE":
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


def process_game_end(state):
    # process end of game
    with open('../../output/results.csv', 'a', newline='') as resultFile:
        writer = csv.writer(resultFile, delimiter=',')
        writer.writerow([state.get_outcome(), state.get_round()])


@post("/")
def index():
    game_json = request.json
    state = state_from_json(game_json)
    print(f'round: {state.get_round()}, points: {state.get_available_points()}, outcome: {state.get_outcome()}')
    if state.get_outcome() == 'pending':
        action = process_round(state)
        print(action.get_json())
        log_to_file(action.get_json())
        log_to_file("")
        return action.get_json()
    else:
        process_game_end(state)
        return end_round()


clear_log_file()

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
port = int(os.getenv('SERVER_PORT', '50123'))
print(f'Pandemic-Player listening to 0.0.0.0:{port}', flush=True)
run(host="0.0.0.0", port=port, quiet=True)

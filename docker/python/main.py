import csv
import importlib
import os

from bottle import post, request, run, BaseRequest

from docker.python.models.actions import end_round
from docker.python.models.gamestate import state_from_json

APPROACH = "random"
LOG_FILE = f'../../output/{APPROACH}_log.txt'


def log_to_file(text):
    if os.getenv('LOG_ACTIONS', 'FALSE') == "TRUE":
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f'{text}\n')


def clear_log_file():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")


def process_round(state):
    approach = importlib.import_module(f'approaches.{APPROACH}')
    return approach.process_round(state)


def process_game_end(state):
    # process end of game
    with open(f'../../output/{APPROACH}_results.csv', 'a', newline='') as resultFile:
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

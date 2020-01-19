import csv
import importlib
import os

from bottle import post, request, run, BaseRequest

from approaches.approach import Approach
from models.actions import end_round
from models.gamestate import state_from_json, GameState

APPROACH = os.getenv('APPROACH', 'combined.combined_city_stats_and_vaccine_random')
LOG_FILE = f'./output/{APPROACH}_log.txt'


def log_to_file(text):
    if os.getenv('LOG_ACTIONS', 'FALSE') == "TRUE":
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f'{text}\n')


def clear_log_file():
    if os.getenv('LOG_ACTIONS', 'FALSE') == "TRUE":
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")


def process_round(state: GameState):
    return approach.process_round(state)


def process_game_end(state):
    # process end of game
    if not os.path.exists('./output'):
        os.mkdir('./output')
    with open(f'./output/{APPROACH}_results.csv', 'a', newline='') as resultFile:
        writer = csv.writer(resultFile, delimiter=',')
        writer.writerow([state.outcome, state.round])


@post("/")
def index():
    game_json = request.json
    state = state_from_json(game_json)
    print(f'round: {state.round}, points: {state.points}, outcome: {state.outcome}')
    if "error" in game_json:
        print(game_json["error"])
    if state.outcome == 'pending':
        action = process_round(state)
        print(action.json)
        log_to_file(action.json)
        log_to_file("")
        return action.json
    else:
        process_game_end(state)
        return end_round()


clear_log_file()

SelectedApproach = getattr(importlib.import_module(f"approaches.{APPROACH}"), APPROACH)
approach: Approach = SelectedApproach()
BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
port = int(os.getenv('SERVER_PORT', '50123'))
print(f'Pandemic-Player listening to 0.0.0.0:{port}', flush=True)
run(host="0.0.0.0", port=port, quiet=True)

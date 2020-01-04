
from bottle import post, request, run, BaseRequest
from models.gamestate import state_from_json
import os

@post("/")
def index():
    game_json = request.json
    print(f'round: {game_json["round"]}, outcome: {game_json["outcome"]}')
    state = state_from_json(game_json)
    print(f'round: {state.get_round()}, outcome: {state.get_outcome()}')
    return {"type": "endRound"}


BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
port = int(os.getenv('SERVER_PORT', '50123'))
print(f'Pandemic-Player listening to 0.0.0.0:{port}', flush=True)
run(host="0.0.0.0", port=port, quiet=True)

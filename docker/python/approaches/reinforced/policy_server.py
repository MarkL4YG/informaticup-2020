import json
import subprocess
import traceback
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

from ray.rllib import ExternalEnv
from ray.rllib.utils.annotations import PublicAPI

from approaches.reinforced.constants import END_EPISODE_RESPONSE, PATH_TO_IC20, INVALID_ACTION
from approaches.reinforced.controller_state import ControllerState
from approaches.reinforced.reward_function import SimpleReward
from models import actions
from models.gamestate import state_from_json, GameState

FIRST_ROUND = 1


@PublicAPI
class PolicyServer(ThreadingMixIn, HTTPServer):

    @PublicAPI
    def __init__(self, external_env: ExternalEnv, address, port):
        socket_address = f'http://{address}:{port}'
        subprocess.Popen([PATH_TO_IC20, '-t', '0', '-u', socket_address, '-o', '/dev/null'])
        handler = _make_handler(external_env, ControllerState(), socket_address)
        HTTPServer.__init__(self, (address, port), handler)


def _make_handler(external_env: ExternalEnv, controller_state: ControllerState, socket_address: str):
    class StatefulHandler(SimpleHTTPRequestHandler):
        """
        Stateful-Handlers are ugly. But I am not going to wrap ic20 inside a policy_client just to make this stateless.
        """
        _controller = controller_state

        def log_message(self, format, *args):
            """
            Silence logging
            """
            return

        # noinspection PyBroadException
        def do_POST(self):
            content_len = int(self.headers.get("Content-Length"), 0)
            request: bytes = self.rfile.read(content_len)
            game_json = json.loads(request.decode())
            try:
                response = self.handle_game(game_json)
                if response == END_EPISODE_RESPONSE:
                    self.connection.close()
                    subprocess.Popen([PATH_TO_IC20, '-t', '0', '-u', socket_address, '-o', '/dev/null'])
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error(500, traceback.format_exc())

        def handle_game(self, game_json: dict):
            state = state_from_json(game_json)

            if not self._controller.is_first_round:
                self.log_reward(state)

            if "error" in game_json:
                print(game_json["error"])
                raise EnvironmentError(game_json["error"])

            self.prepare_new_episode(state)
            return self.handle_round_outcome(state)

        def log_reward(self, state: GameState):
            reward = SimpleReward().calculate_reward(state, controller_state)
            if state.outcome == 'win':
                reward += 500 / state.round
                print(f"Win, "
                      f"Round: {state.round}, "
                      f"Round Reward: {reward}, "
                      f"Invalid-Actions: {self._controller.invalid_action_count}")
            elif state.outcome == 'loss':
                reward -= 500 / state.round
                print(f"Loss, "
                      f"Round: {state.round}, "
                      f"Round Reward: {reward}, "
                      f"Invalid-Actions: {self._controller.invalid_action_count}")
            external_env.log_returns(self._controller.eid, reward)

        # noinspection PyProtectedMember
        def prepare_new_episode(self, state):
            if self._controller.eid in external_env._finished:
                raise RuntimeError(f"Episode {self._controller.eid} was finished already.")

            elif self._controller.eid not in external_env._episodes:
                external_env.start_episode(episode_id=self._controller.eid, training_enabled=True)
                self.update_controller(state)

            else:
                self._controller.is_first_round = False

        def handle_round_outcome(self, state: GameState):
            if state.outcome == 'pending':
                action, action_penalty = external_env.get_action(self._controller.eid, state)
                if action == INVALID_ACTION:
                    action = actions.end_round()
                self.update_controller(state, action_penalty, action == INVALID_ACTION)
                print(action.json)
                return action.json

            elif state.outcome == 'loss':
                external_env.end_episode(self._controller.eid, state)
                self._controller.new_eid()
                self._controller.is_first_round = True
                return END_EPISODE_RESPONSE

            elif state.outcome == 'win':
                external_env.end_episode(self._controller.eid, state)
                self._controller.new_eid()
                self._controller.is_first_round = True
                return END_EPISODE_RESPONSE

            else:
                raise Exception(f"Unknown outcome: {state.outcome}")

        def init_controller(self, state: GameState):
            self.update_controller(state)
            self._controller.invalid_action_count = 0

        def update_controller(self, state: GameState, action_penalty: float = 0, invalid_action=False):
            self._controller.previous_population = state.get_total_population()
            self._controller.previous_infected_population = state.get_total_infected_population()
            self._controller.previous_points = state.points
            self._controller.previous_action_penalty = action_penalty

            if invalid_action:
                self._controller.invalid_action_count += 1

    return StatefulHandler

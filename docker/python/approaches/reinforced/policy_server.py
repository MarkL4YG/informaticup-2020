from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import subprocess
import traceback
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

from ray.rllib import ExternalEnv
from ray.rllib.utils.annotations import PublicAPI

from approaches.reinforced.constants import END_EPISODE_RESPONSE, MAX_CITIES, PATH_TO_IC20
from approaches.reinforced.controller_state import ControllerState
from approaches.reinforced.observation_preprocessors import NaivePreprocessor, ObservationPreprocessor
from approaches.reinforced.reward_function import SimpleReward
from models.gamestate import state_from_json, GameState

FIRST_ROUND = 1


@PublicAPI
class MyServer(ThreadingMixIn, HTTPServer):

    @PublicAPI
    def __init__(self, external_env: ExternalEnv, address, port, preprocessor: ObservationPreprocessor):
        socket_address = f'http://{address}:{port}'
        subprocess.Popen([PATH_TO_IC20, '-t', '0', '-u', socket_address, '-o', '/dev/null'])
        handler = _make_handler(external_env, ControllerState(), socket_address, preprocessor)
        HTTPServer.__init__(self, (address, port), handler)


def _make_handler(external_env: ExternalEnv, controller_state: ControllerState, socket_address: str,
                  preprocessor: ObservationPreprocessor):
    class StatefulHandler(SimpleHTTPRequestHandler):
        """
        Stateful-Handlers are ugly. But I am not going to wrap ic20 inside a policy_client just to make this stateless.
        """
        controller = controller_state
        observation_preprocessor = preprocessor

        # noinspection PyPep8Naming
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
            except Exception:
                self.send_error(500, traceback.format_exc())

        def handle_game(self, game_json: dict):
            state = state_from_json(game_json)

            if not self.controller.is_first_round:
                self.log_reward(state)

            if "error" in game_json:
                print(game_json["error"])
                raise EnvironmentError(game_json["error"])

            self.prepare_new_episode(state)
            return self.handle_round_outcome(state)

        def log_reward(self, state: GameState):
            reward = SimpleReward().calculate_reward(state, controller_state)
            if state.get_outcome() == 'win':
                reward += 100 / state.get_round()
            elif state.get_outcome() == 'loss':
                reward -= 100 / state.get_round()
            external_env.log_returns(self.controller.eid, reward)

        def update_controller(self, state: GameState):
            self.controller.previous_population = state.get_total_population()
            self.controller.previous_infected_population = state.get_total_infected_population()
            self.controller.previous_points = state.get_available_points()

        def prepare_new_episode(self, state):
            if self.controller.eid in external_env._finished:
                raise RuntimeError(f"Episode {self.controller.eid} is finished already.")

            elif self.controller.eid not in external_env._episodes:
                external_env.start_episode(episode_id=self.controller.eid, training_enabled=True)
                self.update_controller(state)

            else:
                self.controller.is_first_round = False

        def handle_round_outcome(self, state: GameState):
            if state.get_outcome() == 'pending':
                action_json, action_observation, action_penalty = external_env.get_action(self.controller.eid,
                                                                                          observation=state)
                self.controller.previous_penalty = action_penalty
                self.update_controller(state)
                return action_json

            elif state.get_outcome() == 'loss':
                external_env.end_episode(self.controller.eid,
                                         self.observation_preprocessor.preprocess(state)[:MAX_CITIES])
                self.controller.new_eid()
                self.controller.is_first_round = True
                return END_EPISODE_RESPONSE

            elif state.get_outcome() == 'win':
                external_env.end_episode(self.controller.eid,
                                         self.observation_preprocessor.preprocess(state)[:MAX_CITIES])
                self.controller.new_eid()
                self.controller.is_first_round = True
                return END_EPISODE_RESPONSE

            else:
                raise Exception(f"Unknown outcome: {state.get_outcome()}")

    return StatefulHandler

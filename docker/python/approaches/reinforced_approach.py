import ray
from ray.rllib.agents import Trainer
from ray.tune import register_env

from approaches.approach import Approach
from approaches.reinforced.action_state_processor import SimpleActStateProcessor
from approaches.reinforced.constants import INVALID_ACTION
from approaches.reinforced.inference_environment import InferenceIC20Environment
from approaches.reinforced.observation_state_processor import SimpleObsStateProcessor, \
    infected_population_sorting_per_city
from models import actions
from models.actions import Action
from models.gamestate import GameState


class ReinforcedApproach(Approach):
    trial_max = 10

    def __init__(self, trainer: Trainer.__class__, weights: str):
        if not ray.is_initialized():
            ray.init()
        self.obs_state_processor = SimpleObsStateProcessor(infected_population_sorting_per_city)
        self.act_state_processor = SimpleActStateProcessor(sort_pathogens=self.obs_state_processor.sort_pathogens)
        register_env("ic20env", lambda _: InferenceIC20Environment(self.obs_state_processor, self.act_state_processor))

        self.trainer = self._load_trainer(trainer(env="ic20env"), weights)

    def process_round(self, state: GameState):
        return self._choose_actionable_action(state)

    def _choose_actionable_action(self, state: GameState) -> Action:
        processed_state = self.obs_state_processor.preprocess_obs(state)
        mapped_action = INVALID_ACTION

        trial_count = 0
        while (mapped_action == INVALID_ACTION or mapped_action.cost > state.points) \
                or mapped_action not in actions.generate_possible_actions(state):
            action = self.trainer.compute_action(observation=processed_state)
            mapped_action, _ = self.act_state_processor.map_action(action, state)

            trial_count += 1
            if trial_count >= self.trial_max:
                mapped_action = actions.end_round()
                break

        return mapped_action

    @classmethod
    def _load_trainer(cls, trainer: Trainer, weights_path: str) -> Trainer:
        trainer.restore(weights_path)
        return trainer
